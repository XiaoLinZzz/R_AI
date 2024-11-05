import logging
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FileAnalysis
import pandas as pd
import traceback
import json
from bson import ObjectId
from django.http import Http404

logger = logging.getLogger(__name__)

# Add JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if pd.isna(obj):
            return None
        if isinstance(obj, pd.Series):
            return obj.to_list()
        if isinstance(obj, pd.Categorical):
            return str(obj)
        if isinstance(obj, complex):
            return f"({obj.real}+{obj.imag}j)"
        return super().default(obj)

class DataProcessingView(APIView):
    def post(self, request):
        file_path = None
        try:
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file uploaded'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            file = request.FILES['file']
            logger.info(f"Processing file: {file.name}")
            
            file_path = default_storage.save(f'temp/{file.name}', file)
            logger.info(f"File saved to: {file_path}")
            
            df = self.infer_and_convert_data_types(file_path)
            logger.info("Data types inferred successfully")
            
            # Replace NaN values with None before serialization
            df = df.replace({pd.NA: None, float('nan'): None})
            
            # Modify data serialization part
            df_dict = df.to_dict(orient='records')
            # Use custom JSONEncoder for serialization
            serialized_data = json.loads(
                json.dumps(df_dict, cls=JSONEncoder, ensure_ascii=False)
            )
            
            # Prepare data, ensure all data is serializable
            analysis_data = {
                'file_name': file.name,
                'data': serialized_data,
                'columns': df.columns.tolist(),
                'dtypes': {str(k): str(v) for k, v in df.dtypes.items()}
            }
            
            file_analysis = FileAnalysis.objects.create(**analysis_data)
            logger.info(f"Analysis saved with ID: {file_analysis._id}")
            
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            return Response({
                'id': str(file_analysis._id),  # 使用 _id
                'file_name': file_analysis.file_name,
                'columns': file_analysis.columns,
                'dtypes': file_analysis.dtypes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            logger.error(traceback.format_exc())
            
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def infer_and_convert_data_types(self, file_path):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Only CSV and Excel files are allowed.")
            
            logger.info(f"File read successfully with {len(df)} rows and {len(df.columns)} columns")

            df.columns = df.columns.astype(str)

            for column in df.columns:
                col_data = df[column].copy()
                
                if col_data.isna().all():
                    continue

                # 1. First check if values are boolean
                bool_values = {'true', 'false'}
                if col_data.dropna().astype(str).str.lower().isin(bool_values).all():
                    df[column] = col_data.map(lambda x: str(x).lower() == 'true' if pd.notna(x) else x)
                    continue

                # 2. Then try to convert to numeric type
                try:
                    numeric_series = pd.to_numeric(col_data, errors='coerce')
                    valid_numbers = numeric_series.notna().sum()
                    # For small datasets (less than 10 records), convert to numeric if 50% are valid numbers
                    threshold = 0.5 if len(col_data) < 100 else 0.8
                    if valid_numbers / col_data.notna().sum() > threshold:
                        if (numeric_series.dropna() % 1 == 0).all():
                            df[column] = numeric_series.astype('Int64')  # Use nullable integer type
                        else:
                            df[column] = numeric_series
                        continue
                except (ValueError, TypeError):
                    pass

                # 3. Check if values are complex numbers
                if col_data.dtype == 'object':
                    complex_pattern = r'^\s*\(?\s*-?\d+\.?\d*\s*[+|-]\s*\d+\.?\d*[ji]\s*\)?\s*$'
                    if col_data.dropna().astype(str).str.match(complex_pattern).all():
                        df[column] = col_data.apply(lambda x: complex(x.strip('()').replace(' ', '')) if pd.notna(x) else x)
                        continue

                # 4. Try to convert to datetime (with stricter validation)
                try:
                    # Check if contains date-related separators
                    date_indicators = ['/', '-', ':']
                    has_date_separators = any(sep in str(x) for sep in date_indicators for x in col_data.dropna().head())
                    
                    if has_date_separators:
                        date_series = pd.to_datetime(col_data, errors='coerce')
                        valid_dates = date_series.notna().sum()
                        # Increase datetime validation threshold to 70%
                        if valid_dates / col_data.notna().sum() > 0.7:
                            df[column] = date_series
                            continue
                except (ValueError, TypeError):
                    pass

                # 5. Check if suitable for categorical type
                if col_data.dtype == 'object':
                    unique_count = col_data.nunique()
                    total_count = len(col_data)
                    
                    # Modified logic:
                    # 1. For data with less than 10 records, convert to category if there are less than 3 unique values
                    # 2. For larger datasets, still use ratio-based judgment
                    if (total_count < 10 and unique_count <= 3) or \
                       (total_count >= 10 and (unique_count / total_count) < 0.5):
                        df[column] = col_data.astype('category')
                        continue

                # 6. Default to string type
                df[column] = col_data.astype(str)

            return df

        except Exception as e:
            logger.error(f"Error in infer_and_convert_data_types: {str(e)}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Error processing the file: {str(e)}")

# Add new view for retrieving analysis results
class GetAnalysisView(APIView):
    def get(self, request, analysis_id):
        try:
            object_id = ObjectId(analysis_id)
            analysis = FileAnalysis.objects.get(_id=object_id)
            
            return Response({
                'id': str(analysis._id),
                'file_name': analysis.file_name,
                'upload_time': analysis.upload_time,
                'dtypes': analysis.dtypes,
                'columns': analysis.columns,
                'data': analysis.data
            })
        except FileAnalysis.DoesNotExist:
            raise Http404("Analysis not found")
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
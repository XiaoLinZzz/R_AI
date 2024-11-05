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

# 添加 JSON 编码器来处理 ObjectId
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
            
            # 修改数据序列化部分
            df_dict = df.to_dict(orient='records')
            # 使用自定义的 JSONEncoder 进行序列化
            serialized_data = json.loads(
                json.dumps(df_dict, cls=JSONEncoder, ensure_ascii=False)
            )
            
            # 准备数据，确保所有数据都是可序列化的
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

                # 1. 首先尝试转换为数值类型（优先级提高）
                try:
                    numeric_series = pd.to_numeric(col_data, errors='coerce')
                    valid_numbers = numeric_series.notna().sum()
                    if valid_numbers / col_data.notna().sum() > 0.8:
                        if (numeric_series.dropna() % 1 == 0).all():
                            df[column] = numeric_series.astype('Int64')
                        else:
                            df[column] = numeric_series
                        continue
                except (ValueError, TypeError):
                    pass

                # 2. 检查是否为复数
                if col_data.dtype == 'object':
                    complex_pattern = r'^\s*\(?\s*-?\d+\.?\d*\s*[+|-]\s*\d+\.?\d*[ji]\s*\)?\s*$'
                    if col_data.dropna().astype(str).str.match(complex_pattern).all():
                        df[column] = col_data.apply(lambda x: complex(x.strip('()').replace(' ', '')) if pd.notna(x) else x)
                        continue

                # 3. 检查是否为布尔值
                bool_values = {'true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0'}
                if col_data.dropna().astype(str).str.lower().isin(bool_values).all():
                    df[column] = col_data.map(lambda x: str(x).lower() in {'true', 't', 'yes', 'y', '1'} if pd.notna(x) else x)
                    continue

                # 4. 尝试转换为日期（添加更严格的判断）
                try:
                    # 检查是否包含日期相关的分隔符
                    date_indicators = ['/', '-', ':']
                    has_date_separators = any(sep in str(x) for sep in date_indicators for x in col_data.dropna().head())
                    
                    if has_date_separators:
                        date_series = pd.to_datetime(col_data, errors='coerce')
                        valid_dates = date_series.notna().sum()
                        # 提高日期判断的阈值到70%
                        if valid_dates / col_data.notna().sum() > 0.7:
                            df[column] = date_series
                            continue
                except (ValueError, TypeError):
                    pass

                # 5. 检查是否适合作为分类
                if col_data.dtype == 'object':
                    unique_ratio = col_data.nunique() / len(col_data)
                    if unique_ratio < 0.5:
                        df[column] = col_data.astype('category')
                        continue

                # 6. 默认保持为字符串类型
                df[column] = col_data.astype(str)

            return df

        except Exception as e:
            logger.error(f"Error in infer_and_convert_data_types: {str(e)}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Error processing the file: {str(e)}")

# 添加新的视图用于获取分析结果
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
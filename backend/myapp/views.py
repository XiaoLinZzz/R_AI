from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import pandas as pd

class DataProcessingView(APIView):
    def post(self, request):
        try:
            print("Request FILES:", request.FILES)
            print("Request POST:", request.POST)
            print("Request content type:", request.content_type)
            
            if 'file' not in request.FILES:
                return Response({'error': 'No file uploaded'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            file_path = default_storage.save(f'temp/{file.name}', file)
            
            df = self.infer_and_convert_data_types(file_path)
            
            result = {
                'data': df.to_dict(orient='records'),
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.apply(lambda x: str(x)).to_dict()
            }
            
            default_storage.delete(file_path)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def infer_and_convert_data_types(self, file_path):
        try:
            # Load the data into a Pandas DataFrame
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Only CSV and Excel files are allowed.")

            # Data type inference and conversion
            for column in df.columns:
                # If column dtype is object, try to infer the actual type
                if df[column].dtype == 'object':
                    try:
                        df[column] = pd.to_datetime(df[column], errors='raise')
                    except (ValueError, TypeError):
                        try:
                            df[column] = pd.to_numeric(df[column], errors='raise')
                        except (ValueError, TypeError):
                            # If both attempts fail, leave it as 'object' (string)
                            pass
                # Convert to category if number of unique values is small compared to total rows
                if df[column].dtype == 'object' and len(df[column].unique()) < 0.05 * len(df):
                    df[column] = df[column].astype('category')
            
            return df

        except Exception as e:
            raise RuntimeError(f"Error processing the file: {e}")
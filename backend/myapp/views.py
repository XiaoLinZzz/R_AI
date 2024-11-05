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
        # Add handling for NaN/Infinity values
        if pd.isna(obj):
            return None
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
            
            # 准备数据，确保所有数据都是可序列化的
            analysis_data = {
                'file_name': file.name,
                'data': json.loads(json.dumps(df.head(100).to_dict(orient='records'), cls=JSONEncoder)),
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

            # 确保所有列名都是字符串类型
            df.columns = df.columns.astype(str)

            # 数据类型转换
            for column in df.columns:
                try:
                    numeric_series = pd.to_numeric(df[column], errors='coerce')
                    if not numeric_series.isna().all():
                        df[column] = numeric_series
                    else:
                        df[column] = df[column].astype(str)  # 转换为字符串以确保可序列化
                except Exception as e:
                    logger.warning(f"Could not convert column {column} to numeric: {str(e)}")
                    df[column] = df[column].astype(str)  # 转换为字符串以确保可序列化

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
                'id': str(analysis._id),  # 使用 _id
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
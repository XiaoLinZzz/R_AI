from django.urls import path
from .views import DataProcessingView, GetAnalysisView

urlpatterns = [
    path('process-data/', DataProcessingView.as_view(), name='process-data'),
    path('analysis/<str:analysis_id>/', GetAnalysisView.as_view(), name='get-analysis'),
]
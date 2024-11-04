from django.urls import path
from .views import DataProcessingView

urlpatterns = [
    path('process-data/', DataProcessingView.as_view(), name='process-data'),
]
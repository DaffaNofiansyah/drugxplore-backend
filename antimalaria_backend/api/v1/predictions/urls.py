from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionViewSet, PredictIC50View, PredictionDownloadView

router = DefaultRouter()
router.register(r'', PredictionViewSet, basename='predictions')


urlpatterns = [
  path('predict/', PredictIC50View.as_view(), name='predict'),
  path('download/<uuid:id>/', PredictionDownloadView.as_view(), name='download'),
  path('', include(router.urls)),
]
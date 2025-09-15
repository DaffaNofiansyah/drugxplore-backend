from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionCompoundViewSet, PredictionCompoundLibView

router = DefaultRouter()
router.register(r'', PredictionCompoundViewSet, basename='prediction_compounds')

urlpatterns = [
    path('lib/', PredictionCompoundLibView.as_view(), name='prediction_compound_lib'),
    path('', include(router.urls)),
]
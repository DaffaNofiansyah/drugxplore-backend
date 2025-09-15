from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('models', views.MLModelViewSet, basename='model')

urlpatterns = [
    path("", include(router.urls)),
    path('predict/', views.PredictIC50View.as_view(), name="predict")
]
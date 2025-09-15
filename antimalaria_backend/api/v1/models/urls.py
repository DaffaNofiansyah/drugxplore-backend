from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivateModelAPIView, MLViewSet

router = DefaultRouter()
router.register(r'', MLViewSet, basename='model')

urlpatterns = [
    path('', include(router.urls)),
    path('activate/<uuid:id>/', ActivateModelAPIView.as_view()),
]
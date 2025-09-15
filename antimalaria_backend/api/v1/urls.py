from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),          # /api/v1/auth/
    path('users/', include('api.v1.users.urls')),          # /api/v1/users/
    path('predictions/', include('api.v1.predictions.urls')), # /api/v1/predictions/
    path('prediction_compounds/', include('api.v1.prediction_compounds.urls')), # /api/v1/prediction_compounds/
    path('models/', include('api.v1.models.urls')),          # /api/v1/models/
]

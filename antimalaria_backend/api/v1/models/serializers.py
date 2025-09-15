from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import MLModel, ModelUpdate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class MLModelSerializer(serializers.ModelSerializer):
    descriptor = serializers.CharField(required=True)
    method = serializers.CharField(required=True)
    file = serializers.FileField(required=True)

    class Meta:
        model = MLModel
        fields = '__all__'
        read_only_fields = ['name', 'version', 'is_active']

class ModelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelUpdate
        fields = '__all__'
from rest_framework import serializers
from api.models import Compound, Prediction, PredictionCompound, MLModel
class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = '__all__' 

class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        exclude = ['created_at']

class PredictionCompoundSerializer(serializers.ModelSerializer):
    compound = CompoundSerializer(read_only=True)
    
    class Meta:
        model = PredictionCompound
        fields = ['id', 'ic50', 'lelp', 'compound']

class PredictionSerializer(serializers.ModelSerializer):
    prediction_compounds = PredictionCompoundSerializer(many=True, read_only=True)
    ml_model = MLModelSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = [
            "id",
            "user",
            "ml_model",
            "input_source_type",
            "created_at",
            "prediction_compounds" 
        ]

from rest_framework import status
from rest_framework.views import APIView
import os
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from api.models import MLModel
from .utils import predict_batch_ic50, load_model

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from api.models import MLModel
from .serializers import MLModelSerializer

class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            model_path = serializer.instance.file.path

            load_model(model_path)

            return Response({
                "status": "success",
                "message": "Model uploaded successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        file_path = instance.file.path  # get file path before deleting DB row
        self.perform_destroy(instance)

        import os
        if os.path.exists(file_path):
            os.remove(file_path)

        return Response(
            {"status": "success", "message": "Model deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class PredictIC50View(APIView):
    def post(self, request, *args, **kwargs):
        smiles_list = request.data.get("smiles", None)
        model_descriptor = request.data.get("model_descriptor", None)
        model_method = request.data.get("model_method", None)

        errors = {}
        if not model_method:
            errors["model_method"] = ["This field is required."]
        if not model_descriptor:
            errors["model_descriptor"] = ["This field is required."]
        if not smiles_list:
            errors["input"] = ["This field is required."]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        ml_model = get_object_or_404(MLModel, descriptor=model_descriptor, method=model_method, is_active=True)

        try:
            predictions = predict_batch_ic50(
                smiles_list=smiles_list,
                model_name=os.path.basename(ml_model.file.name),
                model_descriptor=model_descriptor,
            )
            return Response(predictions, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
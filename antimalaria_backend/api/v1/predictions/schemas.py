from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiTypes
from .serializers import PredictionSerializer, PredictionInputSerializer

# PredictionViewSet schemas
prediction_list_schema = {
    "description": "Get a list of all predictions (admin) or only your own (user).",
    "responses": {
        200: OpenApiResponse(
            description="List of predictions.",
            response=PredictionSerializer(many=True)
        ),
        403: OpenApiResponse(description="Forbidden: User not authenticated.")
    }
}

prediction_retrieve_schema = {
    "description": "Retrieve a specific prediction by its ID.",
    "responses": {
        200: OpenApiResponse(
            description="Prediction details.",
            response=PredictionSerializer
        ),
        403: OpenApiResponse(description="Forbidden: You don't have permission."),
        404: OpenApiResponse(description="Prediction not found."),
    }
}

prediction_destroy_schema = {
    "description": "Delete a prediction.",
    "responses": {
        200: OpenApiResponse(
          description="Deleted successfully.",
          response={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                }
          }
        ),
    }
}

prediction_download_schema = {
    "description": "Download prediction results as a CSV file.",
    "responses": {
        200: OpenApiResponse(
            description="CSV file download initiated.",
            response=OpenApiTypes.BINARY
        ),
        403: OpenApiResponse(description="Forbidden: You don't have permission."),
        404: OpenApiResponse(description="Prediction not found."),
    }
}

predict_ic50_schema = {
    "description": "Submit a comma-separated string/CSV file with SMILES strings to predict IC50 values using the specified ML model.",
    "request": PredictionInputSerializer,
    "responses": {
        200: OpenApiResponse(
            description="Prediction completed successfully.",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Prediction Success",
                    value={
                        "status": "success",
                        "message": "Prediction complete and saved for 2 SMILES.",
                        "data": [
                            {
                                "id": "uuid-of-prediction-1",
                                "smiles": "CCO",
                                "ic50": 5.67,
                                "lelp": 0.45,
                                "category": "very strong",
                                "compound": {
                                    "id": "uuid-of-compound-1",
                                    "name": "Ethanol",
                                    "smiles": "CCO",
                                    "description": "A simple alcohol.",
                                    "inchi": "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3",
                                    "molecular_weight": 46.07,
                                    "inchi_key": "LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
                                    "molecular_formula": "C2H6O"
                                } 
                            },
                            {
                                "id": "uuid-of-prediction-2",
                                "smiles": "CCN",
                                "ic50": 45.23,
                                "lelp": 1.23,
                                "category": "strong",
                                "compound": {
                                    "id": "uuid-of-compound-2",
                                    "name": "Ethylamine",
                                    "smiles": "CCN",
                                    "description": "A simple amine.",
                                    "inchi": "InChI=1S/C2H7N/c1-2-3/h3H,2H2,1H3",
                                    "molecular_weight": 45.08,
                                    "inchi_key": "WQZGKKKJIJFFOK-UHFFFAOYSA-N",
                                    "molecular_formula": "C2H7N"
                                } 
                            }
                        ]
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Bad request.",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Missing Parameters",
                    value={"error": "model_descriptor and model_method are required."}
                )
            ]
        )
    }
}

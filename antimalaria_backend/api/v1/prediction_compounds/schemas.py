# app/schemas.py
from drf_spectacular.utils import OpenApiResponse

# --- PredictionCompound Schemas ---

prediction_compound_list_responses = {
    200: OpenApiResponse(
        description="List of prediction compounds.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/PredictionCompound"}
                }
            }
        }
    ),
    403: OpenApiResponse(description="Permission denied.")
}

prediction_compound_retrieve_responses = {
    200: OpenApiResponse(
        description="Prediction compound details.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {"$ref": "#/components/schemas/PredictionCompound"}
            }
        }
    ),
    404: OpenApiResponse(description="Prediction compound not found."),
    403: OpenApiResponse(description="Permission denied.")
}

prediction_compound_destroy_responses = {
    200: OpenApiResponse(
        description="Prediction compound deleted successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"}
            }
        }
    ),
    404: OpenApiResponse(description="Prediction compound not found."),
    403: OpenApiResponse(description="Permission denied.")
}

prediction_compound_lib_responses = {
    200: OpenApiResponse(
        description="Prediction compound library retrieved successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/PredictionCompound"}
                }
            }
        }
    ),
    403: OpenApiResponse(description="Permission denied.")
}

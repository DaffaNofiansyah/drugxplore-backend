# app/schemas.py
from drf_spectacular.utils import OpenApiResponse, OpenApiExample

# --- Model Schemas ---

model_create_examples = [
    OpenApiExample(
        "Create Model Example",
        value={
            "model_descriptor": "RandomForestClassifier",
            "model_method": "classification",
            "file": "<binary file>"
        },
        request_only=True,
    )
]

model_create_responses = {
    201: OpenApiResponse(
        description="Model created successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "method": {"type": "string"},
                        "descriptor": {"type": "string"},
                        "version": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "created_at": {"type": "string", "format": "date-time"},
                    }
                }
            }
        }
    ),
    400: OpenApiResponse(description="Validation failed"),
    502: OpenApiResponse(description="Failed to store model in backend_model service")
}
model_list_responses = {
    200: OpenApiResponse(
        description="Models retrieved successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "method": {"type": "string"},
                            "descriptor": {"type": "string"},
                            "version": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "created_at": {"type": "string", "format": "date-time"},
                        }
                    }
                }
            }
        }
    ),
    400: OpenApiResponse(description="Validation failed")
}

model_retrieve_responses = {
    200: OpenApiResponse(
        description="Model retrieved successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "method": {"type": "string"},
                        "descriptor": {"type": "string"},
                        "version": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "created_at": {"type": "string", "format": "date-time"},
                    }
                }
            }
        }
    ),
    404: OpenApiResponse(description="Model not found")
}

model_delete_responses = {
    204: OpenApiResponse(
      description="Model deleted successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
            }
        }
    ),
    404: OpenApiResponse(description="Model not found"),
    502: OpenApiResponse(description="Failed to delete model in backend_model service")
}

model_activate_responses = {
    200: OpenApiResponse(
        description="Model activated successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
            }
        }
    ),
    404: OpenApiResponse(description="Model not found")
}

# app/schemas.py
from drf_spectacular.utils import OpenApiResponse, OpenApiExample

# --- Register Schemas ---
register_responses = {
    201: OpenApiResponse(
        description="User registered successfully.",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                    }
                }
            }
        }
    ),
    400: OpenApiResponse(description="Validation failed")
}

register_examples = [
    OpenApiExample(
        "Register Example",
        value={
            "username": "daffa123",
            "email": "daffa@example.com",
            "password": "password123",
            "password2": "password123"
        },
        request_only=True,
    )
]


# --- Login Schemas ---
login_responses = {
    200: OpenApiResponse(
        description="Login successful, JWT token returned",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "refresh": {"type": "string"},
                        "access": {"type": "string"},
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                    }
                }
            }
        }
    ),
    401: OpenApiResponse(description="Invalid credentials"),
}

login_examples = [
    OpenApiExample(
        "Login Example",
        value={
            "username": "daffa123",
            "password": "password123"
        },
        request_only=True
    )
]

# --- Logout Schemas ---
logout_responses = {
    200: OpenApiResponse(
        description="Logout successful",
        response={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
            }
        }
    )
}
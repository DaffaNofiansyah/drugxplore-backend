from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .schemas import register_responses, register_examples, login_responses, login_examples, logout_responses

@extend_schema(
    description="User registration endpoint.",
    request=RegisterSerializer,
    responses=register_responses,
    examples=register_examples
)
class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": "User registered successfully.",
                "data": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    request=LoginSerializer,
    responses=login_responses,
    examples=login_examples
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        return Response({
            "status": "success",
            "message": "Login successful",
            "data": data
        }, status=status.HTTP_200_OK)

@extend_schema(
    description="Logout endpoint to invalidate the refresh token.",
    responses=logout_responses
)
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({
            "status": "success",
            "message": "Logout successful"
        }, status=status.HTTP_200_OK)
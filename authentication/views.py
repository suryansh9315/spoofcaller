import logging
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import uuid4
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, AuthenticationFailed

User = get_user_model()

logger = logging.getLogger(__name__)

def index(request):
    logger.info("Redirecting to login page")
    return redirect('login')

def is_valid_password(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
        raise ValidationError("Password must be alphanumeric (contains both letters and digits).")
    return True

@api_view(['POST'])
@permission_classes([AllowAny])
def register_endpoint(request):
    logger.info("Register endpoint hit with data: %s", request.data)
    
    password = request.data.get("password", "")

    try:
        if password:
            is_valid_password(password)
        else:
            raise ValidationError("Password is required.")
    except ValidationError as e:
        logger.warning("Password validation error: %s", e.message)
        return Response({"errors": e.message}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    try:
        if serializer.is_valid():
            user = serializer.save()
            logger.info("User created successfully: %s", user.phone_number)
            return Response({
                "message": "User created successfully"
            }, status=status.HTTP_201_CREATED)
        logger.error("Validation failed: %s", serializer.errors)
        raise ValidationError(serializer.errors)
    except ValidationError as e:
        logger.warning("Validation error: %s", e.detail)
        return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_endpoint(request):
    logger.info("Login endpoint hit with data: %s", request.data)
    serializer = LoginSerializer(data=request.data)
    try:
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            user = authenticate(request, phone_number=phone_number, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                logger.info("Login successful for user: %s", user.phone_number)
                return Response({
                    "message": "Login successful", 
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_200_OK)
                
            logger.warning("Authentication failed: Invalid credentials for phone number: %s", phone_number)
            raise AuthenticationFailed("Invalid credentials")
        
        logger.error("Validation failed: %s", serializer.errors)
        raise ValidationError(serializer.errors)
    except AuthenticationFailed as e:
        logger.warning("Authentication failed: %s", str(e))
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except ValidationError as e:
        logger.warning("Validation error: %s", e.detail)
        return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_endpoint(request):
    logger.info("Logout endpoint hit for user: %s", request.user.phone_number)
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            logger.warning("No refresh token provided for logout")
            return Response({"error": "Refresh token is required to logout."}, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()  
        logger.info("User logged out and refresh token blacklisted: %s", request.user.phone_number)

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Unexpected error during logout: %s", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_endpoint_v2(request):
    logger.info("Logout endpoint v2 hit for user: %s", request.user.phone_number)
    auth_header = request.headers.get("Authorization", None)

    if auth_header is None:
        logger.warning("Authorization header missing for user: %s", request.user.phone_number)
        return Response(
            {"error": "Authorization header missing"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        token = auth_header.split(" ")[1]
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        logger.info("Authenticated user for logout: %s", user.phone_number)

        refresh_token = request.data.get("refresh_token")
        
        if refresh_token is None:
            logger.warning("No refresh token provided for logout")
            return Response(
                {"error": "Refresh token is required to logout."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist() 
        logger.info("User logged out and refresh token blacklisted: %s", user.phone_number)

        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK,
        )
    
    except IndexError:
        logger.error("Invalid token format provided for logout")
        return Response(
            {"error": "Invalid token format."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as e:
        logger.error("Unexpected error during logout v2: %s", str(e))
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

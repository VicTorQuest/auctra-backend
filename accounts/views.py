from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
    ProfileSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@extend_schema(
    summary="Register a new user",
    description="Creates a new user account and returns the created user's public information.",
    examples=[
        OpenApiExample(
            "Example registration",
            summary="Register a new user",
            description="This request creates a new user with first and last name.",
            value={
                "username": "johndoe",
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "password123",
                "password2": "password123",
            },
        ),
    ],
    responses={
        201: OpenApiExample(
            "Successful registration",
            summary="Example successful response",
            description="Returned when a user is successfully registered.",
            value={
                "message": "Registration successful",
                "user": {
                    "id": 12,
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            },
        ),
        400: {"message": "Invalid data or password mismatch"},
    },
)
class RegisterView(APIView):
    """
    Handles user registration by validating the provided data, creating a new user account,
    and returning a success response with the user's serialized data.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            return Response(
                {"message": "Account created successfully.", "user": user_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Login user and obtain JWT tokens",
    description="Authenticate a user using username and password to receive access and refresh tokens.",
    request=LoginSerializer,
    responses={
        200: OpenApiExample(
            "Successful login",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                },
            },
            response_only=True,
        ),
        401: OpenApiExample(
            "Invalid credentials",
            value={"detail": "Invalid username or password"},
            response_only=True,
        ),
    },
)
class LoginView(APIView):
    """
    Handles user authentication and JWT token generation.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="Logout user by blacklisting refresh token",
    description="Logs out the authenticated user by invalidating their refresh token.",
    examples=[
        OpenApiExample(
            "Example Logout Request",
            value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
        ),
        OpenApiExample(
            "Example Logout Response",
            response_only=True,
            value={"message": "Logout successful"},
        ),
        OpenApiExample(
            "Invalid Token Example",
            response_only=True,
            value={"error": "Invalid token"},
        ),
    ],
)
class LogoutView(APIView):
    """
    Handles user logout by blacklisting the provided refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Account"],
    summary="Get current user",
    description="Retrieve the authenticated user's public information, including nested profile data.",
    responses={200: UserSerializer},
)
class UserView(APIView):
    """
    Retrieve the authenticated user's data including profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Account"],
    summary="Retrieve or update profile",
    description="Get or update the authenticated user's profile (partial updates allowed).",
    request=ProfileSerializer,
    responses={200: ProfileSerializer},
    examples=[
        OpenApiExample(
            "Profile Example (John Doe)",
            summary="Sample profile payload",
            value={
                "wallet_address": "0xabc123...789",
                "category": "gadgets",
                "location_city": "Lagos",
                "location_country": "Nigeria",
                "description": "Trusted gadget reseller.",
                "farcaster_fid": "johndoe.eth",
                "bio": "Web3 trader and marketplace builder.",
                "avatar": "/media/avatars/john.png",
                "is_seller": True,
                "created_at": "2025-10-11T15:24:30Z",
            },
            response_only=True,
        )
    ],
)
class ProfileView(APIView):
    """
    Retrieve or partially update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Request password reset email",
    description="Handles password reset requests by accepting an email and sending a reset link if the account exists.",
    examples=[
        OpenApiExample(
            "Example Password Reset Request",
            value={"email": "johndoe@example.com"},
        ),
        OpenApiExample(
            "Example Success Response",
            response_only=True,
            value={
                "message": "If an account with this email exists, a password reset link has been sent."
            },
        ),
    ],
)
class PasswordResetRequestView(APIView):
    """
    Handles password reset requests by generating a reset token
    and sending an email with the password reset link.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}"
            # reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}&uid={user.pk}"

            # Send the email
            subject = "Password Reset Request"
            message = (
                f"Hi {user.first_name or user.username},\n\n"
                f"We received a request to reset your password.\n"
                f"You can reset it using the link below:\n\n{reset_link}\n\n"
                f"If you didn’t request this, you can safely ignore this email."
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # Do not reveal user existence

        return Response(
            {"message": "If an account with this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Confirm password reset",
    description="Verifies the reset token and allows the user to set a new password.",
    examples=[
        OpenApiExample(
            "Example Reset Confirmation Request",
            value={
                "uidb64": "MTM",  # base64-encoded user ID
                "token": "5e3-2a4b3c1f8ef9d1f51a...",
                "password": "NewStrongPassword123",
                "password2": "NewStrongPassword123",
            },
        ),
        OpenApiExample(
            "Example Successful Response",
            response_only=True,
            value={"message": "Password has been reset successfully."},
        ),
    ],
)
class PasswordResetConfirmView(APIView):
    """
    Handles password reset confirmation by verifying the token
    and setting a new password for the user.
    """

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        password = serializer.validated_data["password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate token
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the new password
        user.set_password(password)
        user.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
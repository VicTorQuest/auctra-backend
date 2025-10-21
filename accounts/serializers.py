from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Profile

User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example Registration Request",
            summary="Register a new user",
            description="Creates a new user account with username, first and last name, email, and password.",
            value={
                "username": "johndoe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "strongpassword123",
                "password2": "strongpassword123",
            },
        ),
        OpenApiExample(
            "Example Registration Response",
            summary="Successful registration response",
            description="Returned data after successful account creation.",
            value={
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            response_only=True,
        ),
    ]
)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example Login Request",
            summary="Login with username and password",
            description="Authenticate an existing user and receive JWT tokens.",
            value={
                "username": "johndoe",
                "password": "strongpassword123",
            },
        ),
        OpenApiExample(
            "Example Login Response",
            summary="Successful login response",
            description="Returns JWT access and refresh tokens with user info.",
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            },
            response_only=True,
        ),
    ]
)
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed("Invalid username or password")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Example Profile',
            summary='User profile example',
            description='Contains extended seller/buyer information for a user.',
            value={
                "wallet_address": "0xabc123...789",
                "category": "gadgets",
                "location_city": "Lagos",
                "location_country": "Nigeria",
                "description": "Trusted gadget reseller.",
                "farcaster_fid": "johndoe.eth",
                "bio": "Web3 trader and marketplace builder.",
                "avatar": "https://example.com/media/avatars/user1.png",
                "is_seller": True,
                "created_at": "2025-10-11T15:24:30Z",
            },
        )
    ]
)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "wallet_address",
            "category",
            "location_city",
            "location_country",
            "description",
            "farcaster_fid",
            "bio",
            "avatar",
            "is_seller",
            "created_at",
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Example User',
            summary='User with profile data',
            value={
                "id": 7,
                "username": "johndoe",
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "profile": {
                    "wallet_address": "0xabc123...789",
                    "category": "gadgets",
                    "location_city": "Lagos",
                    "location_country": "Nigeria",
                    "description": "Trusted gadget reseller.",
                    "farcaster_fid": "vicquest.eth",
                    "bio": "Web3 trader and marketplace builder.",
                    "avatar": "https://example.com/media/avatars/user1.png",
                    "is_seller": True,
                    "created_at": "2025-10-11T15:24:30Z",
                },
            },
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)


    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Password Reset Request',
            summary='Request password reset email',
            description='User submits their registered email address to receive a reset link.',
            value={"email": "johndoe@example.com"},
        )
    ]
)
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Password Reset Confirmation',
            summary='Reset password with token',
            description='Frontend sends token and new password to reset user credentials.',
            value={
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "password": "NewStrongPassword123",
                "password2": "NewStrongPassword123"
            },
        )
    ]
)
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

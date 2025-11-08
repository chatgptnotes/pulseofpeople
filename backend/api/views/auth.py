"""
Authentication Views for Django REST Framework
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from api.models import UserProfile
from api.serializers import RegisterSerializer, UserProfileSerializer, FlexibleLoginSerializer
from api.utils.audit import log_action, ACTION_LOGIN_SUCCESS, ACTION_LOGIN_FAILED, ACTION_USER_CREATED, ACTION_LOGOUT, ACTION_USER_UPDATED, capture_model_state, get_field_changes


# ==================== ROLE HIERARCHY HELPER ====================

# Defines which roles can create which other roles
ROLE_HIERARCHY = {
    'superadmin': ['admin', 'manager', 'analyst', 'user', 'volunteer', 'viewer'],
    'admin': ['manager', 'analyst', 'user', 'volunteer', 'viewer'],
    'manager': ['analyst', 'user', 'volunteer', 'viewer'],
    'analyst': ['user', 'volunteer', 'viewer'],
    'user': [],  # Cannot create users
    'volunteer': [],  # Cannot create users
    'viewer': [],  # Cannot create users
}


def can_create_role(requesting_user_role: str, target_role: str) -> bool:
    """
    Check if a user with requesting_user_role can create a user with target_role

    Args:
        requesting_user_role: Role of the user making the request
        target_role: Role to be assigned to the new user

    Returns:
        bool: True if allowed, False otherwise
    """
    allowed_roles = ROLE_HIERARCHY.get(requesting_user_role, [])
    return target_role in allowed_roles


# ==================== AUTHENTICATION VIEWS ====================

class FlexibleLoginView(APIView):
    """
    Custom login view that accepts EITHER email OR username

    POST /api/auth/login/

    Option 1 - Login with email:
    {
        "email": "user@example.com",
        "password": "password"
    }

    Option 2 - Login with username:
    {
        "username": "johndoe",
        "password": "password"
    }

    Option 3 - Provide both (email takes precedence):
    {
        "username": "johndoe",
        "email": "user@example.com",
        "password": "password"
    }

    Response: {
        "refresh": "refresh_token",
        "access": "access_token"
    }
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = FlexibleLoginSerializer(data=request.data)

        # Get username/email for logging
        username = request.data.get('username', '') or request.data.get('email', '')

        if serializer.is_valid():
            # Login successful - log it
            # The FlexibleLoginSerializer validates and finds the user
            try:
                email = request.data.get('email', '').strip()
                uname = request.data.get('username', '').strip()
                user = None

                if email:
                    user = User.objects.filter(email=email).first()
                elif uname:
                    user = User.objects.filter(username=uname).first()

                if user:
                    log_action(
                        user=user,
                        action=ACTION_LOGIN_SUCCESS,
                        resource_type='Authentication',
                        resource_id='',
                        changes={'username': user.username, 'email': user.email},
                        request=request
                    )
            except Exception:
                pass  # Don't break login if audit logging fails

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        # Login failed - log it
        log_action(
            user=None,
            action=ACTION_LOGIN_FAILED,
            resource_type='Authentication',
            resource_id='',
            changes={'username': username, 'errors': str(serializer.errors)},
            request=request
        )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """
    SECURED User registration endpoint - Requires Authentication
    Only users with appropriate roles can create other users based on hierarchy.

    POST /api/auth/signup/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "email": "user@example.com",
        "password": "securepassword",
        "name": "Full Name",
        "role": "user"  # Role must be in hierarchy allowed by requesting user
    }

    Role Hierarchy:
    - superadmin → can create: admin, manager, analyst, user, volunteer, viewer
    - admin → can create: manager, analyst, user, volunteer, viewer
    - manager → can create: analyst, user, volunteer, viewer
    - analyst → can create: user, volunteer, viewer
    - user/volunteer/viewer → cannot create anyone

    Response: {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "Full Name",
            "role": "user"
        },
        "tokens": {
            "refresh": "eyJ...",
            "access": "eyJ..."
        },
        "message": "User registered successfully"
    }
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)  # SECURED: Requires authentication
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        # Get requesting user's role
        requesting_user = request.user
        requesting_profile = getattr(requesting_user, 'profile', None)
        requesting_role = requesting_profile.role if requesting_profile else 'user'

        # Get target role from request
        target_role = request.data.get('role', 'user')

        # Validate role hierarchy
        if not can_create_role(requesting_role, target_role):
            return Response({
                'error': f'Permission denied. Your role ({requesting_role}) cannot create users with role ({target_role}).',
                'allowed_roles': ROLE_HIERARCHY.get(requesting_role, [])
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Get user profile
        profile = user.profile if hasattr(user, 'profile') else None

        # Log user creation
        log_action(
            user=requesting_user,
            action=ACTION_USER_CREATED,
            resource_type='User',
            resource_id=str(user.id),
            changes={
                'username': user.username,
                'email': user.email,
                'role': profile.role if profile else 'user',
                'created_by': requesting_user.username,
                'created_by_role': requesting_role
            },
            request=request
        )

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'role': profile.role if profile else 'user',
                'permissions': profile.get_permissions() if profile else [],
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully',
            'created_by': f'{requesting_user.username} ({requesting_role})'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get/Update user profile

    GET /api/auth/profile/
    Response: {
        "id": 1,
        "email": "user@example.com",
        "name": "Full Name",
        "role": "user",
        "bio": "",
        "phone": "",
        "avatar": null,
        "assigned_state": null,
        "assigned_district": null
    }
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Get or create profile if it doesn't exist
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'role': 'user'}
        )
        return profile

    def update(self, request, *args, **kwargs):
        # Capture before state
        profile = self.get_object()
        before_state = capture_model_state(profile)

        # Perform update
        response = super().update(request, *args, **kwargs)

        # Capture after state and log changes
        if response.status_code < 400:
            profile.refresh_from_db()
            after_state = capture_model_state(profile)
            field_changes = get_field_changes(before_state, after_state)

            if field_changes:
                log_action(
                    user=request.user,
                    action=ACTION_USER_UPDATED,
                    resource_type='UserProfile',
                    resource_id=str(profile.id),
                    changes={
                        'fields_changed': field_changes,
                        'change_count': len(field_changes)
                    },
                    request=request
                )

        return response


class LogoutView(APIView):
    """
    Logout endpoint (blacklists refresh token)

    POST /api/auth/logout/
    Body: {"refresh": "refresh_token_here"}

    Response: {"message": "Logout successful"}
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Log logout action
            log_action(
                user=request.user,
                action=ACTION_LOGOUT,
                resource_type='Authentication',
                resource_id='',
                changes={'username': request.user.username},
                request=request
            )

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    List users (filtered by role hierarchy)

    GET /api/auth/users/

    Superadmins see all users
    Admins see users below them in hierarchy
    Others see users they created
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        user_role = profile.role if profile else 'user'

        # Superadmin sees all users
        if user_role == 'superadmin':
            return UserProfile.objects.all().select_related('user').order_by('-created_at')

        # Admin sees users below them in hierarchy
        if user_role == 'admin':
            allowed_roles = ['manager', 'analyst', 'user', 'volunteer', 'viewer']
            return UserProfile.objects.filter(role__in=allowed_roles).select_related('user').order_by('-created_at')

        # Manager sees users below them
        if user_role == 'manager':
            allowed_roles = ['analyst', 'user', 'volunteer', 'viewer']
            return UserProfile.objects.filter(role__in=allowed_roles).select_related('user').order_by('-created_at')

        # Analyst sees users below them
        if user_role == 'analyst':
            allowed_roles = ['user', 'volunteer', 'viewer']
            return UserProfile.objects.filter(role__in=allowed_roles).select_related('user').order_by('-created_at')

        # Others see no users
        return UserProfile.objects.none()

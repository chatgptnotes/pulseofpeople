from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, Task, Permission, Notification, UploadedFile, AuditLog


# ==================== AUTHENTICATION SERIALIZERS ====================

class FlexibleLoginSerializer(serializers.Serializer):
    """
    Custom JWT serializer that accepts EITHER email OR username

    Usage:
    - Login with email: {"email": "user@example.com", "password": "pass123"}
    - Login with username: {"username": "johndoe", "password": "pass123"}
    """
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        """Override validate to authenticate with email OR username"""
        username = attrs.get('username', '').strip()
        email = attrs.get('email', '').strip()
        password = attrs.get('password')

        # Check that at least one identifier is provided
        if not username and not email:
            raise serializers.ValidationError('Please provide either username or email.')

        user = None

        # Try to find user by email first (if provided)
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass  # Will try username next or fail later

        # If email didn't work, try username
        if not user and username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass

        # If still no user found, return error
        if not user:
            raise serializers.ValidationError('No user found with the provided credentials.')

        # Authenticate with username and password
        authenticated_user = authenticate(username=user.username, password=password)

        if authenticated_user is None:
            raise serializers.ValidationError('Invalid password.')

        # Check if user is active
        if not authenticated_user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        # Generate JWT tokens using simple-jwt
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(authenticated_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.CharField(write_only=True, required=False, default='user')
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    city = serializers.CharField(write_only=True, required=False, allow_blank=True)
    constituency = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'role', 'phone', 'city', 'constituency']

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role(self, value):
        """Validate role is one of the allowed roles"""
        allowed_roles = ['superadmin', 'admin', 'manager', 'analyst', 'user', 'viewer', 'volunteer']
        if value not in allowed_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {', '.join(allowed_roles)}")
        return value

    def create(self, validated_data):
        """Create user with profile"""
        name = validated_data.pop('name', '')
        role = validated_data.pop('role', 'user')
        phone = validated_data.pop('phone', '')
        city = validated_data.pop('city', '')
        constituency = validated_data.pop('constituency', '')

        # Split name into first/last
        name_parts = name.split(' ', 1) if name else []
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create username from email
        email = validated_data['email']
        username = email.split('@')[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        # Create user profile with role and location info
        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            city=city,
            constituency=constituency
        )

        return user


class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple user serializer for auth responses"""
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'role']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'user'


# ==================== EXISTING SERIALIZERS ====================


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'name', 'role', 'bio', 'avatar', 'avatar_url',
                  'phone', 'date_of_birth', 'permissions', 'assigned_state', 'assigned_district',
                  'city', 'constituency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'permissions']

    def get_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_permissions(self, obj):
        """Get all permissions for this user"""
        return obj.get_permissions()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """Create user with profile"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'owner', 'owner_username', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Auto-assign owner from request user"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for updating user roles (superadmin only)"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id', 'username', 'email']


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for user management (admin/superadmin)"""
    profile = UserProfileSerializer(read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile', 'date_joined', 'last_login', 'is_active']
        read_only_fields = ['id', 'date_joined', 'last_login']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'username', 'title', 'message', 'notification_type',
            'is_read', 'read_at', 'related_model', 'related_id', 'metadata',
            'supabase_id', 'synced_to_supabase', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'supabase_id', 'synced_to_supabase', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Auto-assign user from request"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UploadedFileSerializer(serializers.ModelSerializer):
    """Serializer for uploaded files"""
    username = serializers.CharField(source='user.username', read_only=True)
    file_extension = serializers.SerializerMethodField()
    human_readable_size = serializers.SerializerMethodField()
    is_image = serializers.SerializerMethodField()
    is_video = serializers.SerializerMethodField()
    is_audio = serializers.SerializerMethodField()
    is_document = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = [
            'id', 'user', 'username', 'filename', 'original_filename',
            'file_size', 'mime_type', 'storage_path', 'storage_url',
            'bucket_id', 'file_category', 'metadata',
            'file_extension', 'human_readable_size',
            'is_image', 'is_video', 'is_audio', 'is_document',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_file_extension(self, obj):
        return obj.get_file_extension()

    def get_human_readable_size(self, obj):
        return obj.get_human_readable_size()

    def get_is_image(self, obj):
        return obj.is_image()

    def get_is_video(self, obj):
        return obj.is_video()

    def get_is_audio(self, obj):
        return obj.is_audio()

    def get_is_document(self, obj):
        return obj.is_document()


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'user_email', 'action', 'action_display',
            'target_model', 'target_id', 'changes', 'ip_address', 'user_agent',
            'timestamp'
        ]
        read_only_fields = ['id', 'user', 'timestamp']


class AuditLogListSerializer(serializers.ModelSerializer):
    """Simplified serializer for audit log lists (without changes field)"""
    username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'action', 'action_display',
            'target_model', 'target_id', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'timestamp']

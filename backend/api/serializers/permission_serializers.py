"""
Permission Management Serializers

Serializers for managing user permissions programmatically.
"""
from rest_framework import serializers
from api.models import Permission, UserPermission, RolePermission, UserProfile
from django.contrib.auth.models import User


class PermissionSerializer(serializers.ModelSerializer):
    """Basic permission serializer for listing available permissions"""

    class Meta:
        model = Permission
        fields = ['id', 'name', 'category', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class RolePermissionSerializer(serializers.Serializer):
    """Serializer for role-based permissions"""
    role = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ['role', 'permissions']


class UserPermissionDetailSerializer(serializers.ModelSerializer):
    """Detailed user permission with grant/revoke info"""
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_description = serializers.CharField(source='permission.description', read_only=True)
    permission_category = serializers.CharField(source='permission.category', read_only=True)
    user_email = serializers.EmailField(source='user_profile.user.email', read_only=True)
    granted_by_email = serializers.SerializerMethodField()

    class Meta:
        model = UserPermission
        fields = [
            'id',
            'user_profile',
            'permission',
            'permission_name',
            'permission_description',
            'permission_category',
            'user_email',
            'granted',
            'granted_by_email',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_granted_by_email(self, obj):
        """Get email of user who granted/revoked this permission"""
        # This would require adding a granted_by field to UserPermission model
        # For now, return None
        return None


class UserPermissionsListSerializer(serializers.Serializer):
    """Complete list of user's permissions including role-based and custom"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    role_permissions = serializers.ListField(child=serializers.CharField())
    custom_grants = serializers.ListField(child=serializers.CharField())
    custom_revocations = serializers.ListField(child=serializers.CharField())
    effective_permissions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = [
            'user_id',
            'username',
            'email',
            'role',
            'role_permissions',
            'custom_grants',
            'custom_revocations',
            'effective_permissions'
        ]


class GrantPermissionSerializer(serializers.Serializer):
    """Serializer for granting a permission to a user"""
    permission = serializers.CharField(required=True, help_text="Permission name to grant")
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for granting this permission"
    )

    def validate_permission(self, value):
        """Validate that permission exists"""
        try:
            Permission.objects.get(name=value)
        except Permission.DoesNotExist:
            raise serializers.ValidationError(f"Permission '{value}' does not exist")
        return value

    def validate(self, attrs):
        """Validate grant operation"""
        permission_name = attrs.get('permission')
        request = self.context.get('request')
        target_user_id = self.context.get('target_user_id')

        if not request or not target_user_id:
            raise serializers.ValidationError("Missing request context")

        # Get requesting user's role
        requesting_user = request.user
        requesting_role = requesting_user.profile.role if hasattr(requesting_user, 'profile') else 'user'

        # Get target user
        try:
            target_user = User.objects.get(id=target_user_id)
            target_role = target_user.profile.role if hasattr(target_user, 'profile') else 'user'
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user not found")

        # Cannot modify superadmin permissions
        if target_role == 'superadmin':
            raise serializers.ValidationError("Cannot modify superadmin permissions")

        # Only superadmin can modify own permissions
        if requesting_user.id == target_user.id and requesting_role != 'superadmin':
            raise serializers.ValidationError("Cannot modify your own permissions")

        # Check permission hierarchy
        permission = Permission.objects.get(name=permission_name)

        # System permissions can only be granted by superadmin
        if permission.category == 'system' and requesting_role != 'superadmin':
            raise serializers.ValidationError(
                "Only superadmins can grant system permissions"
            )

        # Check if permission already granted
        existing = UserPermission.objects.filter(
            user_profile=target_user.profile,
            permission__name=permission_name,
            granted=True
        ).exists()

        if existing:
            raise serializers.ValidationError(
                f"Permission '{permission_name}' is already granted to this user"
            )

        # Store validated data for later use
        attrs['_target_user'] = target_user
        attrs['_permission'] = permission
        attrs['_requesting_user'] = requesting_user

        return attrs


class RevokePermissionSerializer(serializers.Serializer):
    """Serializer for revoking a permission from a user"""
    permission = serializers.CharField(required=True, help_text="Permission name to revoke")
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for revoking this permission"
    )

    def validate_permission(self, value):
        """Validate that permission exists"""
        try:
            Permission.objects.get(name=value)
        except Permission.DoesNotExist:
            raise serializers.ValidationError(f"Permission '{value}' does not exist")
        return value

    def validate(self, attrs):
        """Validate revoke operation"""
        permission_name = attrs.get('permission')
        request = self.context.get('request')
        target_user_id = self.context.get('target_user_id')

        if not request or not target_user_id:
            raise serializers.ValidationError("Missing request context")

        # Get requesting user's role
        requesting_user = request.user
        requesting_role = requesting_user.profile.role if hasattr(requesting_user, 'profile') else 'user'

        # Get target user
        try:
            target_user = User.objects.get(id=target_user_id)
            target_role = target_user.profile.role if hasattr(target_user, 'profile') else 'user'
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user not found")

        # Cannot modify superadmin permissions
        if target_role == 'superadmin':
            raise serializers.ValidationError("Cannot modify superadmin permissions")

        # Only superadmin can modify own permissions
        if requesting_user.id == target_user.id and requesting_role != 'superadmin':
            raise serializers.ValidationError("Cannot modify your own permissions")

        # Get permission
        permission = Permission.objects.get(name=permission_name)

        # System permissions can only be revoked by superadmin
        if permission.category == 'system' and requesting_role != 'superadmin':
            raise serializers.ValidationError(
                "Only superadmins can revoke system permissions"
            )

        # Store validated data for later use
        attrs['_target_user'] = target_user
        attrs['_permission'] = permission
        attrs['_requesting_user'] = requesting_user

        return attrs


class SyncRolePermissionsSerializer(serializers.Serializer):
    """Serializer for syncing user permissions to role defaults"""
    confirm = serializers.BooleanField(
        required=True,
        help_text="Must be true to confirm this destructive operation"
    )

    def validate_confirm(self, value):
        """Require explicit confirmation"""
        if not value:
            raise serializers.ValidationError(
                "You must confirm this operation by setting 'confirm' to true"
            )
        return value

    def validate(self, attrs):
        """Validate sync operation"""
        request = self.context.get('request')
        target_user_id = self.context.get('target_user_id')

        if not request or not target_user_id:
            raise serializers.ValidationError("Missing request context")

        # Get requesting user's role
        requesting_user = request.user
        requesting_role = requesting_user.profile.role if hasattr(requesting_user, 'profile') else 'user'

        # Get target user
        try:
            target_user = User.objects.get(id=target_user_id)
            target_role = target_user.profile.role if hasattr(target_user, 'profile') else 'user'
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user not found")

        # Cannot modify superadmin permissions
        if target_role == 'superadmin':
            raise serializers.ValidationError("Cannot sync superadmin permissions")

        # Only superadmin can sync own permissions
        if requesting_user.id == target_user.id and requesting_role != 'superadmin':
            raise serializers.ValidationError("Cannot sync your own permissions")

        # Store validated data
        attrs['_target_user'] = target_user
        attrs['_requesting_user'] = requesting_user

        return attrs

"""
Custom permission classes for role-based access control
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission class to allow only superadmins
    """
    message = "Only superadmins can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile instead of request attribute
        try:
            return request.user.profile.role == 'superadmin'
        except Exception:
            return False


class IsAdminOrAbove(permissions.BasePermission):
    """
    Permission class to allow admins and superadmins
    """
    message = "Only admins and superadmins can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile instead of request attribute
        try:
            return request.user.profile.role in ['admin', 'superadmin']
        except Exception:
            return False


class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow only admins (not superadmins)
    """
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile instead of request attribute
        try:
            return request.user.profile.role == 'admin'
        except Exception:
            return False


class IsManagerOrAbove(permissions.BasePermission):
    """
    Permission class to allow managers, admins, and superadmins
    """
    message = "Only managers and above can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile instead of request attribute
        try:
            return request.user.profile.role in ['manager', 'admin', 'superadmin']
        except Exception:
            return False


class IsAnalystOrAbove(permissions.BasePermission):
    """
    Permission class to allow analysts, managers, admins, and superadmins
    """
    message = "Only analysts and above can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile instead of request attribute
        try:
            return request.user.profile.role in ['analyst', 'manager', 'admin', 'superadmin']
        except Exception:
            return False


class IsUser(permissions.BasePermission):
    """
    Permission class to allow authenticated users
    """
    message = "Authentication required."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwnerOrAdminOrAbove(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object, admins, or superadmins to access it
    """
    message = "You must be the owner or an admin to perform this action."

    def has_object_permission(self, request, view, obj):
        # Superadmins and admins can access everything
        try:
            if request.user.profile.role in ['admin', 'superadmin']:
                return True
        except Exception:
            pass

        # Check if object has owner/user field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class CanManageUsers(permissions.BasePermission):
    """
    Permission for user management:
    - Superadmins can manage everyone
    - Admins can manage regular users only (not other admins or superadmins)
    - Users cannot manage anyone
    """
    message = "You don't have permission to manage users."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superadmins and admins can access user management
        try:
            return request.user.profile.role in ['admin', 'superadmin']
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Check if user can manage the specific user object
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the target user's role
        target_role = None
        if hasattr(obj, 'profile'):
            target_role = obj.profile.role
        elif hasattr(obj, 'role'):
            target_role = obj.role

        # Superadmins can manage everyone
        try:
            if request.user.profile.role == 'superadmin':
                return True
        except Exception:
            pass

        # Admins can only manage regular users (not other admins or superadmins)
        try:
            if request.user.profile.role == 'admin':
                return target_role == 'user'
        except Exception:
            pass

        return False


class CanChangeRole(permissions.BasePermission):
    """
    Only superadmins can change user roles
    """
    message = "Only superadmins can change user roles."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check directly from user profile
        try:
            return request.user.profile.role == 'superadmin'
        except Exception:
            return False


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access to admins and above
    """

    def has_permission(self, request, view):
        # Allow read permissions to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for admins and above
        try:
            return request.user.profile.role in ['admin', 'superadmin']
        except Exception:
            return False


class HasManageRolesPermission(permissions.BasePermission):
    """
    Permission class to check if user has the 'manage_roles' permission.
    Used for permission management endpoints.
    """
    message = "You need 'manage_roles' permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # Superadmins always have this permission
            if request.user.profile.role == 'superadmin':
                return True

            # Check if user has explicit manage_roles permission
            return request.user.profile.has_permission('manage_roles')
        except Exception:
            return False


class CanManagePollingBooths(permissions.BasePermission):
    """
    Permission for polling booth management:
    - Read: Any authenticated user with role-based data isolation
    - Create/Upload: Admin and above
    - Update/Delete: Manager and above
    """
    message = "You don't have permission to manage polling booths."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # GET requests - any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # POST (create/upload) - Admin and above
        if request.method == 'POST':
            try:
                return request.user.profile.role in ['admin', 'superadmin']
            except Exception:
                return False

        # PUT/PATCH/DELETE - Manager and above
        try:
            return request.user.profile.role in ['manager', 'admin', 'superadmin']
        except Exception:
            return False

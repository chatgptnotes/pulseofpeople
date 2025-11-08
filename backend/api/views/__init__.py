"""
Views package
Exports legacy views and role-based views
"""
from .legacy import UserViewSet, UserProfileViewSet, TaskViewSet, NotificationViewSet, UploadedFileViewSet, health_check, profile_me
from .auth import FlexibleLoginView, RegisterView, UserProfileView, LogoutView, UserListView

__all__ = [
    # Legacy views
    "UserViewSet",
    "UserProfileViewSet",
    "TaskViewSet",
    "NotificationViewSet",
    "UploadedFileViewSet",
    "health_check",
    "profile_me",
    # Auth views
    "FlexibleLoginView",
    "RegisterView",
    "UserProfileView",
    "LogoutView",
    "UserListView",
]

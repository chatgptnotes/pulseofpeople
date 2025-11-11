from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import (
    UserViewSet,
    UserProfileViewSet,
    TaskViewSet,
    NotificationViewSet,
    UploadedFileViewSet,
    health_check,
    debug_users,
    create_admin_user,
    profile_me,
    FlexibleLoginView,
    RegisterView,
    UserProfileView,
    LogoutView,
    UserListView,
)
from api.views.user_management import (
    bulk_upload_users,
    bulk_upload_status,
    bulk_upload_errors,
    cancel_bulk_upload,
    download_user_template,
    bulk_upload_jobs_list,
)

# Create router for viewsets (legacy routes)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'files', UploadedFileViewSet, basename='file')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    path('debug/users/', debug_users, name='debug-users'),  # Temporary debug endpoint
    path('debug/create-admin/', create_admin_user, name='create-admin-user'),  # Emergency user creation

    # JWT Authentication - Supports both email and username
    path('auth/login/', FlexibleLoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/signup/', RegisterView.as_view(), name='register'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/users/', UserListView.as_view(), name='user_list'),

    # Profile endpoint
    path('profile/me/', profile_me, name='profile-me'),

    # Bulk User Upload APIs
    path('users/bulk-upload/', bulk_upload_users, name='bulk-upload-users'),
    path('users/bulk-upload/template/', download_user_template, name='bulk-upload-template'),
    path('users/bulk-upload/jobs/', bulk_upload_jobs_list, name='bulk-upload-jobs-list'),
    path('users/bulk-upload/<uuid:job_id>/status/', bulk_upload_status, name='bulk-upload-status'),
    path('users/bulk-upload/<uuid:job_id>/errors/', bulk_upload_errors, name='bulk-upload-errors'),
    path('users/bulk-upload/<uuid:job_id>/', cancel_bulk_upload, name='cancel-bulk-upload'),

    # Role-based routes
    path('superadmin/', include('api.urls.superadmin_urls')),
    path('admin/', include('api.urls.admin_urls')),
    path('user/', include('api.urls.user_urls')),

    # Political Platform APIs (NEW)
    path('', include('api.urls.political_urls')),

    # Core Platform APIs (Workstream 2 - NEW)
    path('', include('api.urls.core_urls')),

    # Geography APIs (Wards and Polling Booths)
    path('geography/', include('api.urls.geography_urls')),

    # News Articles & Sentiment Analysis
    path('news/', include('api.urls.news_urls')),

    # Router URLs (legacy)
    path('', include(router.urls)),
]

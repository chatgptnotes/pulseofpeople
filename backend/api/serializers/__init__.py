# Serializers module
from .geography_serializers import (
    WardSerializer,
    PollingBoothSerializer,
    BulkImportResponseSerializer,
    WardBulkImportSerializer,
    PollingBoothBulkImportSerializer,
)

# Import legacy serializers from serializers_legacy.py
# (Renamed from serializers.py to avoid conflict with this package)
from ..serializers_legacy import (
    UserSerializer,
    UserProfileSerializer,
    TaskSerializer,
    NotificationSerializer,
    UploadedFileSerializer,
    FlexibleLoginSerializer,
    RegisterSerializer,
    SimpleUserSerializer,
    UserRoleSerializer,
    UserManagementSerializer,
)

__all__ = [
    # Geography serializers
    'WardSerializer',
    'PollingBoothSerializer',
    'BulkImportResponseSerializer',
    'WardBulkImportSerializer',
    'PollingBoothBulkImportSerializer',
    # Legacy serializers
    'UserSerializer',
    'UserProfileSerializer',
    'TaskSerializer',
    'NotificationSerializer',
    'UploadedFileSerializer',
    'FlexibleLoginSerializer',
    'RegisterSerializer',
    'SimpleUserSerializer',
    'UserRoleSerializer',
    'UserManagementSerializer',
]

"""
Permission classes for role-based access control
"""
from .role_permissions import (
    IsSuperAdmin,
    IsAdminOrAbove,
    IsAdmin,
    IsManagerOrAbove,
    IsAnalystOrAbove,
    IsUser,
    IsOwnerOrAdminOrAbove,
    CanManageUsers,
    CanChangeRole,
    ReadOnlyOrAdmin,
)

__all__ = [
    'IsSuperAdmin',
    'IsAdminOrAbove',
    'IsAdmin',
    'IsManagerOrAbove',
    'IsAnalystOrAbove',
    'IsUser',
    'IsOwnerOrAdminOrAbove',
    'CanManageUsers',
    'CanChangeRole',
    'ReadOnlyOrAdmin',
]

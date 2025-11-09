# Utils module for Pulse of People backend

# Import functions from parent utils module to make them available
# This resolves the import conflict between utils.py and utils/ package
import sys
import os

# Get the parent directory (api/)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import utils functions from the utils.py module in the api directory
from ..utils import (
    get_user_from_supabase_payload,
    sync_supabase_user,
    handle_user_email_change,
    handle_user_deletion,
    validate_user_role_permissions,
    ensure_user_profile_exists,
)

__all__ = [
    'get_user_from_supabase_payload',
    'sync_supabase_user',
    'handle_user_email_change',
    'handle_user_deletion',
    'validate_user_role_permissions',
    'ensure_user_profile_exists',
]

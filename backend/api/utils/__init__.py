# Utils module for Pulse of People backend

# Import Supabase sync functions from supabase_sync module
# These are the primary utilities used by authentication
from .supabase_sync import (
    get_user_from_supabase_payload,
    sync_supabase_user,
    handle_user_email_change,
    handle_user_deletion,
    validate_user_role_permissions,
    ensure_user_profile_exists,
)

# Note: Other utility modules (validators, excel_exporter, pdf_generator)
# are available but not imported here to avoid unnecessary dependencies
# Import them directly when needed: from api.utils.validators import ...

__all__ = [
    # Supabase sync functions
    'get_user_from_supabase_payload',
    'sync_supabase_user',
    'handle_user_email_change',
    'handle_user_deletion',
    'validate_user_role_permissions',
    'ensure_user_profile_exists',
]

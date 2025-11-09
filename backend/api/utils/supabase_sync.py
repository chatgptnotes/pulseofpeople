"""
Utility functions for API operations
"""

import logging
from django.contrib.auth import get_user_model
from django.db import transaction
from ..models import UserProfile, Organization

User = get_user_model()
logger = logging.getLogger(__name__)


@transaction.atomic
def sync_supabase_user(supabase_user_id, email, user_metadata=None, app_metadata=None):
    """
    Synchronize Supabase user with Django User and UserProfile

    Args:
        supabase_user_id (str): Supabase user UUID
        email (str): User email address
        user_metadata (dict): User metadata from Supabase JWT
        app_metadata (dict): App metadata from Supabase JWT

    Returns:
        User: Django User instance

    Raises:
        ValueError: If email is invalid or missing
    """
    if not email:
        raise ValueError("Email is required for user sync")

    if not supabase_user_id:
        raise ValueError("Supabase user ID is required")

    # Initialize metadata
    user_metadata = user_metadata or {}
    app_metadata = app_metadata or {}

    # Extract user data
    username = user_metadata.get('username') or email.split('@')[0]
    first_name = user_metadata.get('first_name', '')
    last_name = user_metadata.get('last_name', '')
    phone = user_metadata.get('phone', '')
    bio = user_metadata.get('bio', '')
    avatar_url = user_metadata.get('avatar_url', '')

    # Extract role and organization
    role = app_metadata.get('role') or user_metadata.get('role') or 'user'
    organization_id = app_metadata.get('organization_id') or user_metadata.get('organization_id')

    # Validate role
    valid_roles = [choice[0] for choice in UserProfile.ROLE_CHOICES]
    if role not in valid_roles:
        logger.warning(f"Invalid role '{role}' for user {email}, defaulting to 'user'")
        role = 'user'

    # Try to find existing user by email (unique identifier)
    user = None
    user_created = False

    try:
        user = User.objects.get(email=email)
        logger.info(f"Found existing user with email: {email}")

        # Update user fields if they've changed
        updated_fields = []

        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated_fields.append('first_name')

        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated_fields.append('last_name')

        # Update username if it's different and unique
        if username and user.username != username:
            if not User.objects.filter(username=username).exclude(pk=user.pk).exists():
                user.username = username
                updated_fields.append('username')

        if updated_fields:
            user.save(update_fields=updated_fields)
            logger.info(f"Updated user {email} fields: {', '.join(updated_fields)}")

    except User.DoesNotExist:
        # Create new user
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user_created = True
        logger.info(f"Created new user: {email} (username: {username})")

    # Get or create UserProfile
    profile, profile_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': role,
            'bio': bio,
            'phone': phone,
            'avatar_url': avatar_url,
        }
    )

    if profile_created:
        logger.info(f"Created UserProfile for {email} with role: {role}")
    else:
        # Update profile fields if they've changed
        updated = False

        if profile.role != role:
            old_role = profile.role
            profile.role = role
            updated = True
            logger.info(f"Updated role for {email}: {old_role} -> {role}")

        if bio and profile.bio != bio:
            profile.bio = bio
            updated = True

        if phone and profile.phone != phone:
            profile.phone = phone
            updated = True

        if avatar_url and profile.avatar_url != avatar_url:
            profile.avatar_url = avatar_url
            updated = True

        if updated:
            profile.save()
            logger.info(f"Updated UserProfile for {email}")

    # Handle organization assignment
    if organization_id:
        try:
            organization = Organization.objects.get(pk=organization_id)
            if profile.organization != organization:
                profile.organization = organization
                profile.save(update_fields=['organization'])
                logger.info(f"Assigned user {email} to organization: {organization.name}")
        except Organization.DoesNotExist:
            logger.warning(f"Organization {organization_id} not found for user {email}")

    # Log sync operation
    logger.info(
        f"Supabase user sync complete: {email} "
        f"(user_created={user_created}, profile_created={profile_created})"
    )

    return user


def get_user_from_supabase_payload(payload):
    """
    Extract user information from Supabase JWT payload and sync to Django

    Args:
        payload (dict): Decoded Supabase JWT payload

    Returns:
        User: Django User instance

    Raises:
        ValueError: If payload is invalid
    """
    supabase_user_id = payload.get('sub')
    email = payload.get('email')

    if not supabase_user_id or not email:
        raise ValueError('Invalid Supabase payload: missing sub or email')

    user_metadata = payload.get('user_metadata', {})
    app_metadata = payload.get('app_metadata', {})

    return sync_supabase_user(
        supabase_user_id=supabase_user_id,
        email=email,
        user_metadata=user_metadata,
        app_metadata=app_metadata
    )


def handle_user_email_change(old_email, new_email):
    """
    Handle user email changes from Supabase

    Args:
        old_email (str): Previous email address
        new_email (str): New email address

    Returns:
        User: Updated Django User instance

    Raises:
        ValueError: If user not found or new email already exists
    """
    try:
        user = User.objects.get(email=old_email)
    except User.DoesNotExist:
        raise ValueError(f"User with email {old_email} not found")

    # Check if new email already exists
    if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
        raise ValueError(f"User with email {new_email} already exists")

    with transaction.atomic():
        user.email = new_email
        user.save(update_fields=['email'])
        logger.info(f"Updated user email: {old_email} -> {new_email}")

    return user


def handle_user_deletion(email=None, supabase_user_id=None):
    """
    Handle user deletion from Supabase

    Note: This soft-deletes the user by marking them inactive
    instead of hard deletion to preserve audit trails

    Args:
        email (str): User email
        supabase_user_id (str): Supabase user ID

    Returns:
        bool: True if user was deactivated, False if not found
    """
    if not email and not supabase_user_id:
        raise ValueError("Either email or supabase_user_id is required")

    try:
        if email:
            user = User.objects.get(email=email)
        else:
            # If we store supabase_user_id in the future, use it here
            logger.warning("Supabase user ID lookup not implemented")
            return False

        with transaction.atomic():
            user.is_active = False
            user.save(update_fields=['is_active'])

            # Also deactivate the profile if exists
            if hasattr(user, 'profile'):
                # Mark any related records as inactive
                logger.info(f"Deactivated user: {email}")

        return True

    except User.DoesNotExist:
        logger.warning(f"User {email} not found for deletion")
        return False


def validate_user_role_permissions(user, required_role=None, required_permission=None):
    """
    Validate if user has required role or permission

    Args:
        user (User): Django User instance
        required_role (str): Required role (e.g., 'admin', 'manager')
        required_permission (str): Required permission name

    Returns:
        bool: True if user has access, False otherwise
    """
    if not user or not user.is_active:
        return False

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        logger.warning(f"User {user.email} has no profile")
        return False

    # Superadmin always has access
    if profile.is_superadmin():
        return True

    # Check role requirement
    if required_role:
        # Define role hierarchy
        role_hierarchy = {
            'superadmin': 7,
            'admin': 6,
            'manager': 5,
            'analyst': 4,
            'user': 3,
            'viewer': 2,
            'volunteer': 1,
        }

        user_role_level = role_hierarchy.get(profile.role, 0)
        required_role_level = role_hierarchy.get(required_role, 0)

        if user_role_level >= required_role_level:
            return True

    # Check permission requirement
    if required_permission:
        return profile.has_permission(required_permission)

    return False


def ensure_user_profile_exists(user):
    """
    Ensure that a User has a UserProfile
    Creates one if it doesn't exist

    Args:
        user (User): Django User instance

    Returns:
        UserProfile: The user's profile
    """
    from ..models import AuditLog

    try:
        return user.profile
    except UserProfile.DoesNotExist:
        logger.warning(f"Creating missing UserProfile for {user.email}")
        profile = UserProfile.objects.create(
            user=user,
            role='user',  # Default role
        )
        AuditLog.objects.create(
            user=user,
            action='create',
            target_model='UserProfile',
            target_id=str(profile.id),
            changes={
                'auto_created': True,
                'reason': 'Missing profile detected',
            }
        )
        return profile

"""
Django signals for automatic user synchronization and profile management
"""

import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created
    This ensures every User has a corresponding UserProfile
    """
    if created:
        # Check if profile already exists (might be created during sync)
        try:
            # Use get_or_create to avoid duplicate profile errors
            profile, profile_created = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'role': 'user'}  # Default role
            )
            if profile_created:
                logger.info(f"Auto-created UserProfile for user: {instance.email}")
            else:
                logger.info(f"UserProfile already exists for user: {instance.email}")
        except Exception as e:
            logger.error(f"Failed to create UserProfile for {instance.email}: {str(e)}")
            # Don't re-raise - allow user creation to proceed


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Log user creation events to AuditLog
    """
    if created:
        try:
            AuditLog.objects.create(
                user=instance,
                action='create',
                target_model='User',
                target_id=str(instance.id),
                changes={
                    'email': instance.email,
                    'username': instance.username,
                    'created': True,
                }
            )
            logger.info(f"Logged user creation: {instance.email}")
        except Exception as e:
            logger.error(f"Failed to log user creation for {instance.email}: {str(e)}")
            # Don't re-raise - audit logging should not block user creation


@receiver(post_save, sender=UserProfile)
def log_profile_changes(sender, instance, created, **kwargs):
    """
    Log UserProfile creation and updates to AuditLog
    """
    try:
        action = 'create' if created else 'update'
        changes = {
            'role': instance.role,
            'organization': instance.organization.name if instance.organization else None,
        }

        if not created:
            # Track what fields changed
            try:
                if hasattr(instance, 'tracker') and instance.tracker.has_changed('role'):
                    changes['role_changed'] = {
                        'from': instance.tracker.previous('role'),
                        'to': instance.role,
                    }
            except AttributeError:
                # Model doesn't have tracker (field tracking not set up)
                pass

        AuditLog.objects.create(
            user=instance.user,
            action=action,
            target_model='UserProfile',
            target_id=str(instance.id),
            changes=changes
        )
        logger.info(f"Logged UserProfile {action}: {instance.user.email}")
    except Exception as e:
        logger.error(f"Failed to log UserProfile changes for {instance.user.email}: {str(e)}")
        # Don't re-raise - audit logging should not block user creation


@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Log user deletion events
    Note: We use pre_delete because post_delete won't have user info
    """
    try:
        AuditLog.objects.create(
            user=None,  # User is being deleted
            action='delete',
            target_model='User',
            target_id=str(instance.id),
            changes={
                'email': instance.email,
                'username': instance.username,
                'deleted': True,
            }
        )
        logger.warning(f"User deleted: {instance.email}")
    except Exception as e:
        logger.error(f"Failed to log user deletion for {instance.email}: {str(e)}")


@receiver(post_save, sender=UserProfile)
def sync_role_changes_to_supabase(sender, instance, created, **kwargs):
    """
    Optionally sync role changes back to Supabase
    This is a placeholder for future Supabase integration

    Note: Requires Supabase API client setup
    """
    if not created:
        try:
            # Check if role changed
            if hasattr(instance, 'tracker') and instance.tracker.has_changed('role'):
                old_role = instance.tracker.previous('role')
                new_role = instance.role

                logger.info(
                    f"Role changed for {instance.user.email}: {old_role} -> {new_role}"
                )

                # TODO: Implement Supabase sync
                # from supabase import create_client
                # supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                # supabase.auth.admin.update_user_by_id(
                #     user_id,
                #     {"app_metadata": {"role": new_role}}
                # )

        except AttributeError:
            # Model doesn't have tracker
            pass
        except Exception as e:
            logger.error(f"Failed to sync role to Supabase for {instance.user.email}: {str(e)}")


# Note: Helper function moved to utils.py to avoid circular imports
# Import it from there if needed:
# from .utils import ensure_user_profile_exists

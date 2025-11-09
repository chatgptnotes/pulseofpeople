"""
Two-Factor Authentication (2FA) Service
TOTP-based 2FA with QR code generation and backup codes
"""
import pyotp
import qrcode
import io
import base64
import secrets
from django.conf import settings
from django.core.cache import cache


class TwoFactorService:
    """Service for managing 2FA operations"""

    @staticmethod
    def generate_secret_key():
        """Generate a new secret key for TOTP"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(user, secret_key):
        """
        Generate QR code for TOTP setup
        Returns base64 encoded QR code image
        """
        # Create provisioning URI
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user.email,
            issuer_name=getattr(settings, 'APP_NAME', 'Pulse of People')
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'secret_key': secret_key,
            'manual_entry': secret_key,
        }

    @staticmethod
    def verify_totp_code(secret_key, code):
        """
        Verify TOTP code
        Returns True if code is valid
        """
        totp = pyotp.TOTP(secret_key)
        return totp.verify(code, valid_window=1)  # Allow 1 time step before/after

    @staticmethod
    def generate_backup_codes(count=10):
        """
        Generate backup codes for 2FA recovery
        Returns list of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX
            formatted_code = f'{code[:4]}-{code[4:]}'
            codes.append(formatted_code)

        return codes

    @staticmethod
    def hash_backup_code(code):
        """Hash backup code for storage"""
        from django.contrib.auth.hashers import make_password
        # Remove dashes before hashing
        clean_code = code.replace('-', '')
        return make_password(clean_code)

    @staticmethod
    def verify_backup_code(stored_hash, provided_code):
        """Verify backup code against stored hash"""
        from django.contrib.auth.hashers import check_password
        # Remove dashes before checking
        clean_code = provided_code.replace('-', '')
        return check_password(clean_code, stored_hash)

    @staticmethod
    def is_2fa_required_for_role(role):
        """
        Check if 2FA is required for a given role
        Mandatory for admin and superadmin, optional for others
        """
        required_roles = ['superadmin', 'admin', 'manager']
        return role in required_roles

    @staticmethod
    def setup_2fa_for_user(user):
        """
        Complete 2FA setup for a user
        Returns secret key, QR code, and backup codes
        """
        # Generate secret key
        secret_key = TwoFactorService.generate_secret_key()

        # Generate QR code
        qr_data = TwoFactorService.generate_qr_code(user, secret_key)

        # Generate backup codes
        backup_codes = TwoFactorService.generate_backup_codes()

        # Store in user profile (you'll need to add these fields to UserProfile model)
        user.profile.totp_secret = secret_key
        user.profile.is_2fa_enabled = False  # Will be enabled after verification
        user.profile.save()

        # Hash and store backup codes
        from api.models import TwoFactorBackupCode
        TwoFactorBackupCode.objects.filter(user=user).delete()  # Clear old codes

        for code in backup_codes:
            TwoFactorBackupCode.objects.create(
                user=user,
                code_hash=TwoFactorService.hash_backup_code(code)
            )

        return {
            'secret_key': secret_key,
            'qr_code': qr_data['qr_code'],
            'manual_entry': qr_data['manual_entry'],
            'backup_codes': backup_codes,
        }

    @staticmethod
    def enable_2fa_for_user(user, verification_code):
        """
        Enable 2FA after verifying setup code
        Returns True if successful
        """
        if not user.profile.totp_secret:
            return False, 'No 2FA setup found. Please setup 2FA first.'

        # Verify the code
        if not TwoFactorService.verify_totp_code(user.profile.totp_secret, verification_code):
            return False, 'Invalid verification code'

        # Enable 2FA
        user.profile.is_2fa_enabled = True
        user.profile.save()

        return True, '2FA enabled successfully'

    @staticmethod
    def disable_2fa_for_user(user, password):
        """
        Disable 2FA for a user (requires password confirmation)
        """
        # Verify password
        if not user.check_password(password):
            return False, 'Invalid password'

        # Disable 2FA
        user.profile.is_2fa_enabled = False
        user.profile.totp_secret = None
        user.profile.save()

        # Delete backup codes
        from api.models import TwoFactorBackupCode
        TwoFactorBackupCode.objects.filter(user=user).delete()

        return True, '2FA disabled successfully'

    @staticmethod
    def verify_2fa_code(user, code):
        """
        Verify 2FA code (TOTP or backup code)
        Returns tuple (success, message)
        """
        if not user.profile.is_2fa_enabled:
            return False, '2FA is not enabled for this user'

        # First try TOTP code
        if TwoFactorService.verify_totp_code(user.profile.totp_secret, code):
            return True, 'TOTP code verified'

        # Then try backup code
        from api.models import TwoFactorBackupCode
        backup_codes = TwoFactorBackupCode.objects.filter(user=user, is_used=False)

        for backup_code in backup_codes:
            if TwoFactorService.verify_backup_code(backup_code.code_hash, code):
                # Mark backup code as used
                backup_code.is_used = True
                backup_code.save()
                return True, 'Backup code verified'

        return False, 'Invalid 2FA code'

    @staticmethod
    def regenerate_backup_codes(user):
        """
        Regenerate backup codes for a user
        Returns new backup codes
        """
        if not user.profile.is_2fa_enabled:
            return None, '2FA is not enabled'

        # Delete old backup codes
        from api.models import TwoFactorBackupCode
        TwoFactorBackupCode.objects.filter(user=user).delete()

        # Generate new codes
        backup_codes = TwoFactorService.generate_backup_codes()

        # Hash and store
        for code in backup_codes:
            TwoFactorBackupCode.objects.create(
                user=user,
                code_hash=TwoFactorService.hash_backup_code(code)
            )

        return backup_codes, 'Backup codes regenerated'

    @staticmethod
    def get_2fa_status(user):
        """Get 2FA status for a user"""
        try:
            return {
                'is_enabled': user.profile.is_2fa_enabled,
                'is_required': TwoFactorService.is_2fa_required_for_role(user.profile.role),
                'has_backup_codes': user.twofactor_backup_codes.filter(is_used=False).exists(),
            }
        except AttributeError:
            return {
                'is_enabled': False,
                'is_required': False,
                'has_backup_codes': False,
            }


# Model for storing backup codes (add this to models.py)
"""
class TwoFactorBackupCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='twofactor_backup_codes')
    code_hash = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'Used' if self.is_used else 'Active'
        return f'{self.user.username} - Backup Code ({status})'
"""

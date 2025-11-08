"""
Management command to seed permissions and role-permission mappings
Aligned with frontend permissions.ts (67 permissions across 9 categories)
"""
from django.core.management.base import BaseCommand
from api.models import Permission, RolePermission


class Command(BaseCommand):
    help = 'Seeds permissions and role-permission mappings (67 permissions total)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding permissions...')
        self.stdout.write('=' * 60)

        # Define all 67 permissions organized by category
        # Matches frontend/src/utils/permissions.ts exactly
        permissions_data = [
            # ===== USER MANAGEMENT (5 permissions) =====
            {'name': 'view_users', 'category': 'users', 'description': 'View list of users in organization'},
            {'name': 'create_users', 'category': 'users', 'description': 'Invite and create new users'},
            {'name': 'edit_users', 'category': 'users', 'description': 'Edit user information and roles'},
            {'name': 'delete_users', 'category': 'users', 'description': 'Remove users from organization'},
            {'name': 'manage_roles', 'category': 'users', 'description': 'Create and assign roles'},

            # ===== DATA MANAGEMENT (7 permissions) =====
            {'name': 'view_dashboard', 'category': 'data', 'description': 'Access main dashboard'},
            {'name': 'view_analytics', 'category': 'data', 'description': 'Access analytics and reports'},
            {'name': 'view_reports', 'category': 'data', 'description': 'Access detailed reports'},
            {'name': 'export_data', 'category': 'data', 'description': 'Export data to CSV/Excel'},
            {'name': 'import_data', 'category': 'data', 'description': 'Import data from files'},
            {'name': 'create_surveys', 'category': 'data', 'description': 'Create and manage surveys'},
            {'name': 'view_surveys', 'category': 'data', 'description': 'View survey results'},

            # ===== VOTER MANAGEMENT (3 permissions) =====
            {'name': 'view_voters', 'category': 'data', 'description': 'Access voter database'},
            {'name': 'edit_voters', 'category': 'data', 'description': 'Edit voter information'},
            {'name': 'delete_voters', 'category': 'data', 'description': 'Remove voter records'},

            # ===== FIELD WORKERS (4 permissions) =====
            {'name': 'view_field_workers', 'category': 'data', 'description': 'View field worker list'},
            {'name': 'manage_field_workers', 'category': 'data', 'description': 'Add/remove field workers'},
            {'name': 'view_field_reports', 'category': 'data', 'description': 'View reports from field'},
            {'name': 'submit_field_reports', 'category': 'data', 'description': 'Submit field reports'},

            # ===== SOCIAL MEDIA (2 permissions) =====
            {'name': 'view_social_media', 'category': 'data', 'description': 'Access social media monitoring'},
            {'name': 'manage_social_channels', 'category': 'data', 'description': 'Add/remove social channels'},

            # ===== COMPETITOR ANALYSIS (1 permission) =====
            {'name': 'view_competitor_analysis', 'category': 'analytics', 'description': 'Access competitor data'},

            # ===== AI & INSIGHTS (2 permissions) =====
            {'name': 'view_ai_insights', 'category': 'analytics', 'description': 'Access AI-generated insights'},
            {'name': 'generate_ai_insights', 'category': 'analytics', 'description': 'Trigger AI analysis'},

            # ===== SETTINGS (3 permissions) =====
            {'name': 'view_settings', 'category': 'settings', 'description': 'View organization settings'},
            {'name': 'edit_settings', 'category': 'settings', 'description': 'Modify organization settings'},
            {'name': 'manage_billing', 'category': 'settings', 'description': 'Access billing and subscription'},

            # ===== ALERTS (2 permissions) =====
            {'name': 'view_alerts', 'category': 'data', 'description': 'View system alerts'},
            {'name': 'manage_alerts', 'category': 'data', 'description': 'Create and configure alerts'},

            # ===== SYSTEM (Super Admin only - 4 permissions) =====
            {'name': 'manage_organizations', 'category': 'system', 'description': 'Create/delete organizations'},
            {'name': 'view_all_data', 'category': 'system', 'description': 'Access data across all organizations'},
            {'name': 'manage_system_settings', 'category': 'system', 'description': 'Configure platform-wide settings'},
            {'name': 'view_audit_logs', 'category': 'system', 'description': 'Access system audit logs'},
        ]

        # Create permissions
        created_count = 0
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                name=perm_data['name'],
                defaults={
                    'category': perm_data['category'],
                    'description': perm_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created permission: {perm.name}'))
            else:
                self.stdout.write(f'  - Permission exists: {perm.name}')

        self.stdout.write(self.style.SUCCESS(f'\nCreated {created_count} new permissions'))
        self.stdout.write(f'Total permissions: {Permission.objects.count()}')

        # Define role-permission mappings
        # Based on frontend DEFAULT_ROLE_PERMISSIONS and role hierarchy
        role_permissions_map = {
            # SUPERADMIN - Has ALL 33 permissions (handled by is_superadmin() check, but stored for completeness)
            'superadmin': [
                # User Management (5)
                'view_users', 'create_users', 'edit_users', 'delete_users', 'manage_roles',
                # Data Management (7)
                'view_dashboard', 'view_analytics', 'view_reports', 'export_data', 'import_data',
                'create_surveys', 'view_surveys',
                # Voter Management (3)
                'view_voters', 'edit_voters', 'delete_voters',
                # Field Workers (4)
                'view_field_workers', 'manage_field_workers', 'view_field_reports', 'submit_field_reports',
                # Social Media (2)
                'view_social_media', 'manage_social_channels',
                # Competitor Analysis (1)
                'view_competitor_analysis',
                # AI & Insights (2)
                'view_ai_insights', 'generate_ai_insights',
                # Settings (3)
                'view_settings', 'edit_settings', 'manage_billing',
                # Alerts (2)
                'view_alerts', 'manage_alerts',
                # System (4 - superadmin only)
                'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs',
            ],

            # ADMIN - All except system permissions (29 permissions)
            'admin': [
                # User Management (5)
                'view_users', 'create_users', 'edit_users', 'delete_users', 'manage_roles',
                # Data Management (7)
                'view_dashboard', 'view_analytics', 'view_reports', 'export_data', 'import_data',
                'create_surveys', 'view_surveys',
                # Voter Management (3)
                'view_voters', 'edit_voters', 'delete_voters',
                # Field Workers (4)
                'view_field_workers', 'manage_field_workers', 'view_field_reports', 'submit_field_reports',
                # Social Media (2)
                'view_social_media', 'manage_social_channels',
                # Competitor Analysis (1)
                'view_competitor_analysis',
                # AI & Insights (2)
                'view_ai_insights', 'generate_ai_insights',
                # Settings (3)
                'view_settings', 'edit_settings', 'manage_billing',
                # Alerts (2)
                'view_alerts', 'manage_alerts',
                # NO system permissions
            ],

            # MANAGER - User management + analytics + field workers (14 permissions)
            'manager': [
                # User Management (limited - no delete, no roles)
                'view_users', 'create_users', 'edit_users',
                # Data Management
                'view_dashboard', 'view_analytics', 'view_reports', 'export_data',
                'create_surveys', 'view_surveys',
                # Field Workers
                'view_field_workers', 'manage_field_workers', 'view_field_reports',
                # Alerts
                'view_alerts',
            ],

            # ANALYST - Analytics + reporting + social media (10 permissions)
            'analyst': [
                # Data Management
                'view_dashboard', 'view_analytics', 'view_reports', 'export_data',
                'view_surveys',
                # Field Reports (view only)
                'view_field_reports',
                # Social Media
                'view_social_media',
                # Competitor Analysis
                'view_competitor_analysis',
                # AI & Insights
                'view_ai_insights',
                # Alerts
                'view_alerts',
            ],

            # USER - Basic dashboard + tasks (6 permissions)
            'user': [
                'view_dashboard', 'view_analytics', 'view_reports',
                'view_surveys', 'view_field_reports', 'view_alerts',
            ],

            # VIEWER - Read-only access (4 permissions)
            'viewer': [
                'view_dashboard', 'view_analytics', 'view_reports', 'view_alerts',
            ],

            # VOLUNTEER - Data collection only (3 permissions)
            'volunteer': [
                'view_dashboard', 'submit_field_reports', 'view_surveys',
            ],
        }

        # Create role-permission mappings
        self.stdout.write('\nSeeding role-permission mappings...')
        mapping_count = 0

        for role, permission_names in role_permissions_map.items():
            for perm_name in permission_names:
                try:
                    permission = Permission.objects.get(name=perm_name)
                    role_perm, created = RolePermission.objects.get_or_create(
                        role=role,
                        permission=permission
                    )
                    if created:
                        mapping_count += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ! Permission not found: {perm_name}')
                    )

        self.stdout.write(self.style.SUCCESS(f'\nCreated {mapping_count} new role-permission mappings'))
        self.stdout.write(f'Total mappings: {RolePermission.objects.count()}')

        # Display detailed summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ RBAC SETUP COMPLETE - 33 PERMISSIONS ALIGNED WITH FRONTEND'))
        self.stdout.write('='*70)

        # Permission breakdown by category
        self.stdout.write('\n' + self.style.WARNING('PERMISSION BREAKDOWN BY CATEGORY:'))
        self.stdout.write('-' * 70)

        categories = {
            'users': 'User Management',
            'data': 'Data & Field Operations',
            'analytics': 'Analytics & Insights',
            'settings': 'Settings',
            'system': 'System (Superadmin Only)',
        }

        for cat_key, cat_name in categories.items():
            count = Permission.objects.filter(category=cat_key).count()
            self.stdout.write(f'  {cat_name.ljust(30)}: {count} permissions')

        total = Permission.objects.count()
        self.stdout.write('-' * 70)
        self.stdout.write(self.style.SUCCESS(f'  TOTAL PERMISSIONS: {total}'))

        # Role-permission mapping summary
        self.stdout.write('\n' + self.style.WARNING('ROLE-PERMISSION MAPPINGS:'))
        self.stdout.write('-' * 70)

        role_descriptions = {
            'superadmin': 'Super Administrator (Platform Owner)',
            'admin': 'Administrator (Organization Owner)',
            'manager': 'Manager (User + Analytics + Field)',
            'analyst': 'Analyst (Analytics + Reports + Social)',
            'user': 'User (Basic Dashboard + Reports)',
            'viewer': 'Viewer (Read-Only Access)',
            'volunteer': 'Volunteer (Data Collection Only)',
        }

        for role in ['superadmin', 'admin', 'manager', 'analyst', 'user', 'viewer', 'volunteer']:
            perm_count = RolePermission.objects.filter(role=role).count()
            role_desc = role_descriptions.get(role, role)
            self.stdout.write(f'  {role.ljust(12)}: {str(perm_count).rjust(2)} permissions - {role_desc}')

        # Permission categories in database
        self.stdout.write('\n' + self.style.WARNING('DATABASE CONFIGURATION:'))
        self.stdout.write('-' * 70)
        self.stdout.write(f'  Permission Model: api.models.Permission')
        self.stdout.write(f'  RolePermission Model: api.models.RolePermission')
        self.stdout.write(f'  UserPermission Model: api.models.UserPermission (custom overrides)')

        self.stdout.write('\n' + self.style.WARNING('NOTES:'))
        self.stdout.write('-' * 70)
        self.stdout.write('  • Superadmin has ALL permissions (enforced in code)')
        self.stdout.write('  • System permissions (4) are superadmin-only')
        self.stdout.write('  • Role hierarchy: superadmin > admin > manager > analyst > user > viewer > volunteer')
        self.stdout.write('  • Custom user permissions override role defaults via UserPermission model')
        self.stdout.write('  • Re-running this command is safe (idempotent)')

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ Backend permissions now aligned with frontend/src/utils/permissions.ts'))
        self.stdout.write('='*70 + '\n')

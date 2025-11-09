from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Import signals when Django starts
        This ensures signal handlers are registered
        """
        import api.signals  # noqa: F401

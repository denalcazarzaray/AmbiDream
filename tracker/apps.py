from django.apps import AppConfig


class AmbidreamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AmbiDream'

    def ready(self):
        """Import signals when app is ready"""
        import tracker.signals
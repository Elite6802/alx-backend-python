from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self):
        """
        Import the signals module to connect the receivers when the app is ready.
        """
        import messaging.signals # noqa: F401
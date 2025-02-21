from django.apps import AppConfig


class AppBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_bot'
    verbose_name = 'Influencer Marketing Bot'

    def ready(self):
        """
        Initialize any app-specific settings or signals here.
        This method is called when the app is ready.
        """
        try:
            # Import and register signals
            import app_bot.signals
        except ImportError:
            pass 
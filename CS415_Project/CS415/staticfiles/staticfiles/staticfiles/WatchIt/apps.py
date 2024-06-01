from django.apps import AppConfig


class WatchitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WatchIt'

    def ready(self):
        import WatchIt.signals

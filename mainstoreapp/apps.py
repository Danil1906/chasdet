from django.apps import AppConfig


class MainstoreappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainstoreapp'

    def ready(self):
        import mainstoreapp.signals

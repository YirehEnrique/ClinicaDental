from django.apps import AppConfig


class DentistaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dentista'
    def ready(self):
        import dentista.signals
from django.apps import AppConfig

class config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from .models import DocumentFolderPath
        DocumentFolderPath.create_default_instance()

from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # El parche va aquí, cuando las apps ya están listas
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        
        user_logged_in.disconnect(update_last_login)

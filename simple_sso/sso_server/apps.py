from django.apps import AppConfig


class SimpleSSOServer(AppConfig):
    name = 'simple_sso.sso_server'
    # Django < 6.0 defaults to AutoField for auto-created primary keys.
    # Django 6.0+ defaults to BigAutoField for auto-created primary keys.
    # Define default_auto_field attribute to avoid type changes and tricky migrations.
    default_auto_field = "django.db.models.AutoField"

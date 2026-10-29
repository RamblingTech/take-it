from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Registers the "core" app: settings and pieces shared by the whole of TAKE IT."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "TAKE IT settings"

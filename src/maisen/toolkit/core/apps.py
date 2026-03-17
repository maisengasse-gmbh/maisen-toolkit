from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "maisen.toolkit.core"
    label = "maisen_core"
    verbose_name = "Maisen Core"

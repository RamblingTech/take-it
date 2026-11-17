from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Registers the "inventory" app: devices and everything that describes them."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"
    verbose_name = "Inventory"

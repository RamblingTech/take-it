"""
views.py for the inventory app: the Python functions that build the
device pages.
"""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from core.roles import ALL_ROLES, role_required

from .models import Category, CustomField, Device, Location, Status


@role_required(*ALL_ROLES)  # Any of the four roles can look at devices.
def device_list(request):
    """The list of all devices, with a search box and filters."""

    # Start with every device. select_related fetches the model, status,
    # holder and location in the same database trip (much faster).
    devices = Device.objects.select_related(
        "model__manufacturer", "model__category", "status", "current_holder", "current_location",
    )

    # request.GET holds whatever is after the "?" in the address,
    # e.g. /devices/?q=dell&status=2  ->  q="dell", status="2".
    search = request.GET.get("q", "").strip()
    status_id = request.GET.get("status", "")
    category_id = request.GET.get("category", "")
    location_id = request.GET.get("location", "")

    if search:
        # Q(...) | Q(...) means "this OR that". icontains = "contains, ignoring upper/lower case".
        devices = devices.filter(
            Q(asset_tag__icontains=search)
            | Q(serial__icontains=search)
            | Q(name__icontains=search)
            | Q(model__name__icontains=search)
            | Q(model__manufacturer__name__icontains=search)
            | Q(current_holder__name__icontains=search)
        )
    if status_id:
        devices = devices.filter(status_id=status_id)
    if category_id:
        devices = devices.filter(model__category_id=category_id)
    if location_id:
        devices = devices.filter(current_location_id=location_id)

    # Show 50 devices per page, with Next/Previous buttons.
    page = Paginator(devices, 50).get_page(request.GET.get("page"))

    context = {
        "page": page,
        "search": search,
        "statuses": Status.objects.all(),
        "categories": Category.objects.all(),
        "locations": Location.objects.all(),
        "selected": {"status": status_id, "category": category_id, "location": location_id},
    }

    # When HTMX asks (live search), send back ONLY the table, not the whole page.
    # (A "history restore" is the browser's Back button: that needs the whole page.)
    if request.headers.get("HX-Request") and not request.headers.get("HX-History-Restore-Request"):
        return render(request, "inventory/_device_table.html", context)
    return render(request, "inventory/device_list.html", context)


@role_required(*ALL_ROLES)
def device_detail(request, pk):
    """One device's page: its details, custom fields, and full history."""

    # pk is the device's ID number from the address, e.g. /devices/7/.
    # get_object_or_404: if there's no such device, show "Page not found".
    device = get_object_or_404(
        Device.objects.select_related("model__manufacturer", "model__category", "status",
                                      "current_holder", "current_location", "created_by"),
        pk=pk,
    )

    # Pair each custom field with this device's value for it (blank if none).
    custom_fields = [(field, device.custom_data.get(field.key, "")) for field in CustomField.objects.all()]

    history = device.activity.select_related("person", "location", "status", "user")

    return render(request, "inventory/device_detail.html", {
        "device": device,
        "custom_fields": custom_fields,
        "history": history,
    })

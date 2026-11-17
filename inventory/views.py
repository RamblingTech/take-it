"""
views.py for the inventory app: the Python functions that build the
device pages.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import ADMIN, ALL_ROLES, TECHNICIAN, role_required

from .forms import DeviceForm
from .models import ActivityLog, Category, CustomField, Device, Location, Status


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


@role_required(ADMIN, TECHNICIAN)  # Only Admins and Technicians can add devices.
def device_create(request):
    """The "Add device" page."""

    # A web page is first shown with GET. When "Save" is clicked, the
    # filled-in form comes back with POST.
    if request.method == "POST":
        form = DeviceForm(request.POST)
        # is_valid() runs all the checks. If any fail, the page is shown
        # again with the problems marked in red.
        if form.is_valid():
            device = form.save(commit=False)
            device.created_by = request.user
            device.save()
            ActivityLog.record(device, ActivityLog.CREATED, user=request.user)
            # A one-time green message shown on the next page.
            messages.success(request, f"Device {device.asset_tag} was added.")
            return redirect("device_detail", pk=device.pk)
    else:
        # Start with a blank form, with "Ready to Deploy" picked as the status.
        form = DeviceForm(initial={"status": Status.objects.filter(name="Ready to Deploy").first()})

    return render(request, "inventory/device_form.html", {"form": form, "device": None})


@role_required(ADMIN, TECHNICIAN)
def device_edit(request, pk):
    """The "Edit device" page."""

    device = get_object_or_404(Device, pk=pk)
    # Remember the status before any changes, so we can tell if it changed.
    old_status = device.status

    if request.method == "POST":
        # instance=device: fill the form from this device, and save changes back to it.
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            if device.status != old_status:
                ActivityLog.record(device, ActivityLog.STATUS_CHANGE, user=request.user,
                                   notes=f"{old_status} → {device.status}")
            if form.has_changed():
                ActivityLog.record(device, ActivityLog.UPDATED, user=request.user,
                                   notes="Changed: " + ", ".join(form[name].label for name in form.changed_data))
            messages.success(request, f"Device {device.asset_tag} was saved.")
            return redirect("device_detail", pk=device.pk)
    else:
        form = DeviceForm(instance=device)

    return render(request, "inventory/device_form.html", {"form": form, "device": device})


@role_required(ADMIN)  # Only Admins can delete. Technicians never see this page.
def device_delete(request, pk):
    """Asks "are you sure?" first; the device is only deleted when that's confirmed (POST)."""

    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        tag = device.asset_tag
        device.delete()
        messages.success(request, f"Device {tag} was deleted.")
        return redirect("device_list")
    return render(request, "inventory/device_confirm_delete.html", {"device": device})

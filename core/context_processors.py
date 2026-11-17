"""
A "context processor" adds values to EVERY page automatically.

This one makes the Organization (company name, logo) available to all
templates as {{ organization }}, so the header can always show it.
"""

from .models import Organization
from .roles import ADMIN, TECHNICIAN, user_has_role


def organization(request):
    return {"organization": Organization.load()}


def permissions(request):
    """
    Yes/no answers every page can use to decide which buttons to show,
    e.g. {% if can_edit_devices %} ... {% endif %}.
    (The views still check roles too, so hiding a button is never the only lock.)
    """
    return {
        "can_edit_devices": user_has_role(request.user, ADMIN, TECHNICIAN),
        "is_admin": user_has_role(request.user, ADMIN),
    }

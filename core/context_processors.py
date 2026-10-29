"""
A "context processor" adds values to EVERY page automatically.

This one makes the Organization (company name, logo) available to all
templates as {{ organization }}, so the header can always show it.
"""

from .models import Organization


def organization(request):
    return {"organization": Organization.load()}

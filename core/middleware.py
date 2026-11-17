"""
Middleware: code that runs on every web request, before the page is built.

This one switches TAKE IT's clock to the company's time zone (from the
Organization settings), so every date and time on screen is local time.
"""

import zoneinfo

from django.utils import timezone

from .models import Organization


class OrganizationTimezoneMiddleware:
    def __init__(self, get_response):
        # Django hands us the "next step" once, when the server starts.
        self.get_response = get_response

    def __call__(self, request):
        # For this request, show times in the company's time zone...
        timezone.activate(zoneinfo.ZoneInfo(Organization.load().default_timezone))
        # ...then carry on and build the page as normal.
        return self.get_response(request)

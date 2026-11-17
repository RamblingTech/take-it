"""
views.py holds the "views": Python functions that build a page.

A view receives the visitor's request, gathers any data the page needs,
and hands it to a template (the HTML) to display.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .roles import ALL_ROLES, user_has_role


@login_required  # Not logged in? Django sends you to the login page first.
def home(request):
    """The page you land on after logging in."""

    # Make a list of the role names this user has, e.g. ["Technician"].
    my_roles = [role for role in ALL_ROLES if user_has_role(request.user, role)]

    # render() fills in the template with these values and returns the page.
    # (is_admin for the admin button comes from core/context_processors.py.)
    return render(request, "core/home.html", {"my_roles": my_roles})

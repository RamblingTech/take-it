"""
roles.py defines TAKE IT's four roles and the tools for checking them.

Each role is a Django "Group". A user is given a role by being added to
that group (on the admin pages: Users > pick a user > Groups).
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# The four role names. Using these constants (instead of typing the name
# each time) means a typo shows up as an error instead of a silent bug.
ADMIN = "Admin"
TECHNICIAN = "Technician"
FINANCE = "Finance"
MANAGEMENT = "Management"

ALL_ROLES = [ADMIN, TECHNICIAN, FINANCE, MANAGEMENT]


def user_has_role(user, *roles):
    """
    Answer True or False: does this user have at least one of these roles?

    Example: user_has_role(request.user, ADMIN, TECHNICIAN)
    A superuser (the account made with createsuperuser) always counts as Admin.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser and ADMIN in roles:
        return True
    return user.groups.filter(name__in=roles).exists()


def role_required(*roles):
    """
    Put @role_required(...) above a page's view to lock that page to these roles.

    Not logged in?           -> sent to the login page.
    Logged in, wrong role?   -> "403 Forbidden" (access denied).
    """

    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not user_has_role(request.user, *roles):
                raise PermissionDenied
            return view_function(request, *args, **kwargs)

        return wrapper

    return decorator

from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def admin_required(view_func):
    """Membatasi halaman Admin Center untuk user staff/superuser."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Halaman tersebut hanya dapat diakses admin.")
            return redirect("user:user_index")
        return view_func(request, *args, **kwargs)

    return wrapper

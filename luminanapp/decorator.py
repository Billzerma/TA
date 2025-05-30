from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Anda belum login.")
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Anda tidak memiliki akses.")
        return _wrapped_view
    return decorator

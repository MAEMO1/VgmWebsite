"""Convenience decorators to protect Django views."""

from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponseForbidden

from .rbac import has_capability


def require_capability(capability: str, mosque_kwarg: str = 'mosque_id') -> Callable:
    """Protect a function-based view with a capability check."""

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped(request: HttpRequest, *args, **kwargs):
            mosque_id = kwargs.get(mosque_kwarg)
            if not has_capability(getattr(request, 'user', None), capability, mosque_id):
                return HttpResponseForbidden('Forbidden')
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator

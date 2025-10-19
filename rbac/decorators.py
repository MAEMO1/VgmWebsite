"""Convenience decorators to protect Flask views."""

from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify

from .rbac import has_capability


def require_capability(capability: str, mosque_kwarg: str = 'mosque_id') -> Callable:
    """Protect a Flask route with a capability check."""

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            mosque_id = kwargs.get(mosque_kwarg)
            if not has_capability(getattr(request, 'user', None), capability, mosque_id):
                return jsonify({'error': 'Forbidden'}), 403
            return view_func(*args, **kwargs)

        return wrapped

    return decorator

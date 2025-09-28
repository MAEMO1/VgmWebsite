"""Reusable DRF permission class leveraging the RBAC engine."""

from rest_framework.permissions import BasePermission

from .rbac import has_capability


class HasCapability(BasePermission):
    """Check a capability (optionally scoped to a mosque id kwarg)."""

    message = 'You do not have permission to perform this action.'

    def __init__(self, capability: str, mosque_kwarg: str = 'mosque_id') -> None:
        self.capability = capability
        self.mosque_kwarg = mosque_kwarg

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        kwargs = getattr(view, 'kwargs', {}) or getattr(getattr(request, 'parser_context', {}), 'get', lambda _: {})('kwargs') or {}
        mosque_id = kwargs.get(self.mosque_kwarg)
        return has_capability(getattr(request, 'user', None), self.capability, mosque_id)

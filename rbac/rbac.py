"""Role-based access control helpers for Flask services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from models import User

Grant = Tuple[str, Optional[str]]  # (capability, scope | None)


def _load_rbac_config() -> Dict[str, Dict[str, List]]:
    config_path = Path(__file__).resolve().parents[1] / 'config' / 'rbac.config.json'
    with config_path.open('r', encoding='utf-8') as fh:
        raw_config = json.load(fh)

    roles: Dict[str, Dict[str, List]] = {}
    for role, definition in raw_config['roles'].items():
        extends: List[str] = definition.get('extends', [])
        grant_strings: List[str] = definition.get('grants', [])
        parsed_grants: List[Grant] = []
        for grant_str in grant_strings:
            cap, _, scope = grant_str.partition(':')
            parsed_grants.append((cap, scope or None))
        roles[role] = {'extends': extends, 'grants': parsed_grants}
    return roles


RBAC = _load_rbac_config()


def _flatten(role: str, seen: Optional[Set[str]] = None) -> Set[Grant]:
    seen = seen or set()
    if role in seen:
        return set()
    seen.add(role)
    definition = RBAC[role]
    grants: Set[Grant] = set(definition["grants"])
    for parent in definition["extends"]:
        grants |= _flatten(parent, seen)
    return grants


def user_grants(user: Optional[User]) -> Set[Grant]:
    role = (user.role if user and hasattr(user, 'role') else "GAST")
    return _flatten(role)


def has_capability(user: Optional[User], capability: str, mosque_id: Optional[str] = None) -> bool:
    if not user:
        return capability == "content.view_public"
    if hasattr(user, 'role') and user.role == "BEHEERDER":
        return True

    grants = [grant for grant in user_grants(user) if grant[0] == capability]
    if not grants:
        return False

    if any(scope in (None, "any", "platform") for _, scope in grants):
        return True

    if any(scope == "own" for _, scope in grants):
        return bool(mosque_id) and hasattr(user, 'manages_mosque') and user.manages_mosque(mosque_id)

    return False

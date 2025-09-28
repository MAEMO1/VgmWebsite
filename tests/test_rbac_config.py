import json
from pathlib import Path

import pytest

from rbac import rbac


@pytest.mark.parametrize('role', ['GAST', 'LID', 'MOSKEE_BEHEERDER', 'BEHEERDER'])
def test_python_rbac_matches_config(role):
    config_path = Path(__file__).resolve().parents[1] / 'config' / 'rbac.config.json'
    raw = json.loads(config_path.read_text(encoding='utf-8'))
    config_definition = raw['roles'][role]
    expected_extends = config_definition.get('extends', [])
    expected_grants = []
    for grant in config_definition.get('grants', []):
        cap, _, scope = grant.partition(':')
        expected_grants.append((cap, scope or None))

    python_definition = rbac.RBAC[role]
    assert python_definition['extends'] == expected_extends

    # normalise grants (cap, scope|None)
    normalised_python = sorted(python_definition['grants'])
    normalised_config = sorted(expected_grants)
    assert normalised_python == normalised_config


def test_has_capability_uses_scope(monkeypatch):
    class DummyUser:
        role = 'MOSKEE_BEHEERDER'

        def manages_mosque(self, mosque_id: str) -> bool:
            return mosque_id == 'own'

    user = DummyUser()
    assert rbac.has_capability(user, 'mosque.manage', mosque_id='own')
    assert not rbac.has_capability(user, 'mosque.manage', mosque_id='other')

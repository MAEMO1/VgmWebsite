"""Integration tests for RBAC system with Flask app."""

import os
import pytest
from unittest.mock import Mock, patch

# Set environment before importing main
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from main import app, db
from rbac import rbac


@pytest.fixture
def client():
    """Create test client."""
    import os
    os.environ['FLASK_ENV'] = 'testing'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def mock_user():
    """Create mock user for testing."""
    user = Mock()
    user.role = 'LID'
    user.manages_mosque = Mock(return_value=False)
    return user


@pytest.fixture
def mock_admin():
    """Create mock admin user for testing."""
    admin = Mock()
    admin.role = 'BEHEERDER'
    admin.manages_mosque = Mock(return_value=True)
    return admin


@pytest.fixture
def mock_mosque_manager():
    """Create mock mosque manager for testing."""
    manager = Mock()
    manager.role = 'MOSKEE_BEHEERDER'
    manager.manages_mosque = Mock(return_value=True)
    return manager


class TestRBACIntegration:
    """Test RBAC integration with Flask app."""
    
    def test_guest_capabilities(self):
        """Test guest user capabilities."""
        user = None
        assert rbac.has_capability(user, 'content.view_public')
        assert not rbac.has_capability(user, 'profile.manage')
        assert not rbac.has_capability(user, 'site.admin')
    
    def test_member_capabilities(self, mock_user):
        """Test member user capabilities."""
        assert rbac.has_capability(mock_user, 'content.view_public')
        assert rbac.has_capability(mock_user, 'profile.manage')
        assert rbac.has_capability(mock_user, 'events.register')
        assert not rbac.has_capability(mock_user, 'site.admin')
    
    def test_mosque_manager_capabilities(self, mock_mosque_manager):
        """Test mosque manager capabilities."""
        # Mock the manages_mosque method to return True for 'own'
        mock_mosque_manager.manages_mosque = Mock(return_value=True)
        
        assert rbac.has_capability(mock_mosque_manager, 'mosque.manage', mosque_id='own')
        assert rbac.has_capability(mock_mosque_manager, 'events.manage', mosque_id='own')
        
        # Mock the manages_mosque method to return False for 'other'
        mock_mosque_manager.manages_mosque = Mock(return_value=False)
        assert not rbac.has_capability(mock_mosque_manager, 'mosque.manage', mosque_id='other')
        assert not rbac.has_capability(mock_mosque_manager, 'site.admin')
    
    def test_admin_capabilities(self, mock_admin):
        """Test admin user capabilities."""
        assert rbac.has_capability(mock_admin, 'site.admin')
        assert rbac.has_capability(mock_admin, 'users.manage')
        assert rbac.has_capability(mock_admin, 'mosque.manage', mosque_id='any')
        assert rbac.has_capability(mock_admin, 'analytics.view_platform')
    
    def test_role_hierarchy(self, mock_user, mock_mosque_manager, mock_admin):
        """Test role hierarchy inheritance."""
        # All roles should have guest capabilities
        assert rbac.has_capability(mock_user, 'content.view_public')
        assert rbac.has_capability(mock_mosque_manager, 'content.view_public')
        assert rbac.has_capability(mock_admin, 'content.view_public')
        
        # Members and above should have member capabilities
        assert rbac.has_capability(mock_user, 'profile.manage')
        assert rbac.has_capability(mock_mosque_manager, 'profile.manage')
        assert rbac.has_capability(mock_admin, 'profile.manage')
        
        # Only admins should have admin capabilities
        assert not rbac.has_capability(mock_user, 'site.admin')
        assert not rbac.has_capability(mock_mosque_manager, 'site.admin')
        assert rbac.has_capability(mock_admin, 'site.admin')
    
    def test_scope_handling(self, mock_mosque_manager):
        """Test scope-based access control."""
        # Mock the manages_mosque method to return True for 'mosque1'
        mock_mosque_manager.manages_mosque = Mock(side_effect=lambda mosque_id: mosque_id == 'mosque1')
        
        # Should have access to own mosque
        assert rbac.has_capability(mock_mosque_manager, 'mosque.manage', mosque_id='mosque1')
        
        # Should not have access to other mosques
        assert not rbac.has_capability(mock_mosque_manager, 'mosque.manage', mosque_id='mosque2')
        
        # Should not have access without mosque_id
        assert not rbac.has_capability(mock_mosque_manager, 'mosque.manage')
    
    def test_capability_grants(self, mock_user):
        """Test capability grants for different roles."""
        grants = rbac.user_grants(mock_user)
        grant_strings = [f"{cap}:{scope}" if scope else cap for cap, scope in grants]
        
        # Should have member capabilities
        assert 'profile.manage' in grant_strings
        assert 'events.register' in grant_strings
        assert 'donations.use' in grant_strings
        
        # Should not have admin capabilities
        assert 'site.admin' not in grant_strings
        assert 'users.manage' not in grant_strings
    
    def test_undefined_capability(self, mock_user):
        """Test handling of undefined capabilities."""
        # Should return False for undefined capabilities
        assert not rbac.has_capability(mock_user, 'undefined.capability')
        assert not rbac.has_capability(None, 'undefined.capability')
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with None user
        assert rbac.has_capability(None, 'content.view_public')
        assert not rbac.has_capability(None, 'profile.manage')
        
        # Test with empty mosque_id
        user = Mock()
        user.role = 'MOSKEE_BEHEERDER'
        user.manages_mosque = Mock(return_value=False)
        
        assert not rbac.has_capability(user, 'mosque.manage', mosque_id='')
        assert not rbac.has_capability(user, 'mosque.manage', mosque_id=None)

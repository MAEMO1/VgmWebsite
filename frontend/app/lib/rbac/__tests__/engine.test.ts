import { hasCapability, userGrants } from '../engine';
import type { AuthUser } from '../types';

describe('RBAC Engine', () => {
  const mockGuest = null;
  const mockLid: AuthUser = {
    id: 'lid-1',
    role: 'LID',
    emailVerified: true,
    twoFAEnabled: false,
  };
  const mockMosqueManager: AuthUser = {
    id: 'manager-1',
    role: 'MOSKEE_BEHEERDER',
    emailVerified: true,
    twoFAEnabled: false,
    managedMosqueIds: ['mosque-1'],
  };
  const mockAdmin: AuthUser = {
    id: 'admin-1',
    role: 'BEHEERDER',
    emailVerified: true,
    twoFAEnabled: true,
  };

  describe('Guest capabilities', () => {
    it('should allow public content access', () => {
      expect(hasCapability(mockGuest, 'content.view_public')).toBe(true);
    });

    it('should deny member-only content', () => {
      expect(hasCapability(mockGuest, 'profile.manage')).toBe(false);
      expect(hasCapability(mockGuest, 'events.register')).toBe(false);
    });
  });

  describe('LID capabilities', () => {
    it('should inherit guest capabilities', () => {
      expect(hasCapability(mockLid, 'content.view_public')).toBe(true);
    });

    it('should have member capabilities', () => {
      expect(hasCapability(mockLid, 'profile.manage')).toBe(true);
      expect(hasCapability(mockLid, 'events.register')).toBe(true);
      expect(hasCapability(mockLid, 'donations.use')).toBe(true);
    });

    it('should not have admin capabilities', () => {
      expect(hasCapability(mockLid, 'site.admin')).toBe(false);
      expect(hasCapability(mockLid, 'users.manage')).toBe(false);
    });
  });

  describe('MOSKEE_BEHEERDER capabilities', () => {
    it('should inherit LID capabilities', () => {
      expect(hasCapability(mockMosqueManager, 'profile.manage')).toBe(true);
      expect(hasCapability(mockMosqueManager, 'events.register')).toBe(true);
    });

    it('should have mosque management for own mosque', () => {
      expect(hasCapability(mockMosqueManager, 'mosque.manage', { mosqueId: 'mosque-1' })).toBe(true);
      expect(hasCapability(mockMosqueManager, 'events.manage', { mosqueId: 'mosque-1' })).toBe(true);
    });

    it('should not have mosque management for other mosques', () => {
      expect(hasCapability(mockMosqueManager, 'mosque.manage', { mosqueId: 'mosque-2' })).toBe(false);
    });

    it('should not have admin capabilities', () => {
      expect(hasCapability(mockMosqueManager, 'site.admin')).toBe(false);
    });
  });

  describe('BEHEERDER capabilities', () => {
    it('should have all capabilities', () => {
      expect(hasCapability(mockAdmin, 'site.admin')).toBe(true);
      expect(hasCapability(mockAdmin, 'users.manage')).toBe(true);
      expect(hasCapability(mockAdmin, 'analytics.view_platform')).toBe(true);
    });

    it('should have mosque management for any mosque', () => {
      expect(hasCapability(mockAdmin, 'mosque.manage', { mosqueId: 'any-mosque' })).toBe(true);
    });
  });

  describe('User grants', () => {
    it('should return correct grants for LID', () => {
      const grants = userGrants(mockLid);
      const grantStrings = Array.from(grants);
      
      expect(grantStrings).toContain('content.view_public');
      expect(grantStrings).toContain('profile.manage');
      expect(grantStrings).toContain('events.register');
      expect(grantStrings).not.toContain('site.admin');
    });

    it('should return correct grants for MOSKEE_BEHEERDER', () => {
      const grants = userGrants(mockMosqueManager);
      const grantStrings = Array.from(grants);
      
      expect(grantStrings).toContain('mosque.manage:own');
      expect(grantStrings).toContain('events.manage:own');
      expect(grantStrings).not.toContain('site.admin');
    });
  });
});

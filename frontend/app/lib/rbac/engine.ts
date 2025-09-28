import { RBAC } from './config';
import type { AuthUser, Capability, Grant, Role } from './types';

function flattenGrants(role: Role, seen = new Set<Role>()): Set<Grant> {
  if (seen.has(role)) return new Set();
  seen.add(role);
  const def = RBAC.roles[role];
  const grants = new Set<Grant>(def.grants);
  for (const parent of def.extends) {
    for (const g of flattenGrants(parent, seen)) {
      grants.add(g);
    }
  }
  return grants;
}

function parseGrant(grant: Grant): { cap: Capability; scope?: 'own' | 'any' | 'platform' } {
  const [cap, scope] = grant.split(':') as [Capability, 'own' | 'any' | 'platform' | undefined];
  return { cap, scope };
}

export function userGrants(user: AuthUser | null | undefined): Set<Grant> {
  const role = user?.role ?? 'GAST';
  return flattenGrants(role);
}

export function hasCapability(
  user: AuthUser | null | undefined,
  capability: Capability,
  options?: { mosqueId?: string }
): boolean {
  if (!user) return capability === 'content.view_public';
  if (user.role === 'BEHEERDER') return true;

  const grants = userGrants(user);
  const matches = [...grants].map(parseGrant).filter((g) => g.cap === capability);
  if (matches.length === 0) return false;

  if (matches.some((g) => g.scope === undefined || g.scope === 'any' || g.scope === 'platform')) {
    return true;
  }

  if (matches.some((g) => g.scope === 'own')) {
    const mosqueId = options?.mosqueId;
    return !!mosqueId && (user.managedMosqueIds ?? []).includes(mosqueId);
  }

  return false;
}

export const canManageMosque = (user: AuthUser | null | undefined, mosqueId: string) =>
  hasCapability(user, 'mosque.manage', { mosqueId });

export const canViewPlatformAnalytics = (user: AuthUser | null | undefined) =>
  hasCapability(user, 'analytics.view_platform');

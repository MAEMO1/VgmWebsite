import type { AuthUser as RbacUser } from './types';

export type FrontendRole = 'admin' | 'mosque_admin' | 'user' | null | undefined;

export function mapFrontendRole(role: FrontendRole): RbacUser['role'] {
  switch (role) {
    case 'admin':
      return 'BEHEERDER';
    case 'mosque_admin':
      return 'MOSKEE_BEHEERDER';
    case 'user':
      return 'LID';
    default:
      return 'GAST';
  }
}

export function createAuthUser(params: {
  id: string;
  role: FrontendRole;
  managedMosqueIds?: string[];
  emailVerified: boolean;
  twoFAEnabled: boolean;
}): RbacUser {
  return {
    id: params.id,
    role: mapFrontendRole(params.role),
    managedMosqueIds: params.managedMosqueIds ?? [],
    emailVerified: params.emailVerified,
    twoFAEnabled: params.twoFAEnabled,
  };
}

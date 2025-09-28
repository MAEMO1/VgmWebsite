'use client';

import { useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import type { AuthUser } from '../lib/rbac/types';
import { createAuthUser } from '../lib/rbac/transform';

export function useRbacUser(): AuthUser | null {
  const { user } = useAuth();

  return useMemo(() => {
    if (!user) return null;
    return createAuthUser({
      id: String(user.id),
      role: user.role,
      managedMosqueIds: user.mosque_id ? [String(user.mosque_id)] : [],
      emailVerified: user.email_verified,
      twoFAEnabled: false,
    });
  }, [user]);
}

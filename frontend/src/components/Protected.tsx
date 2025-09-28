'use client';

import React from 'react';
import { hasCapability } from '../lib/rbac/engine';
import type { AuthUser, Capability } from '../lib/rbac/types';

type ProtectedProps = {
  user: AuthUser | null;
  capability: Capability;
  mosqueId?: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
};

export function Protected({ user, capability, mosqueId, children, fallback = null }: ProtectedProps) {
  const allowed = hasCapability(user, capability, { mosqueId });
  return allowed ? <>{children}</> : <>{fallback}</>;
}

import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { ROLE_ORDER } from '@/lib/rbac/config';
import type { AuthUser } from '@/lib/rbac/types';

function getAuthUserFromRequest(req: NextRequest): AuthUser | null {
  const roleCookie = req.cookies.get('x-role')?.value as AuthUser['role'] | undefined;
  if (!roleCookie) return null;
  const managedMosque = req.cookies.get('x-mosque')?.value;
  return {
    id: 'mock-user',
    role: roleCookie,
    emailVerified: true,
    twoFAEnabled: roleCookie === 'BEHEERDER',
    managedMosqueIds: managedMosque ? [managedMosque] : [],
  };
}

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const user = getAuthUserFromRequest(req);

  const redirectTo = (target: string) => {
    const url = req.nextUrl.clone();
    url.pathname = target;
    return NextResponse.redirect(url);
  };

  if (pathname === '/dashboard' || pathname === '/dashboard/') {
    if (!user) return redirectTo('/auth/signin');
    if (user.role === 'LID') return redirectTo('/dashboard/main');
    if (user.role === 'MOSKEE_BEHEERDER') return redirectTo('/dashboard/mosque-dashboard');
    if (user.role === 'BEHEERDER') return redirectTo('/dashboard/admin');
  }

  if (pathname.startsWith('/dashboard/admin')) {
    if (!user || user.role !== 'BEHEERDER') return redirectTo('/auth/signin');
  }

  if (pathname.startsWith('/dashboard/mosque-dashboard')) {
    if (!user || (user.role !== 'MOSKEE_BEHEERDER' && user.role !== 'BEHEERDER')) {
      return redirectTo('/auth/signin');
    }
  }

  const membersOnlyPrefixes = ['/dashboard/main', '/notificaties', '/dashboard/profiel'];
  if (membersOnlyPrefixes.some((prefix) => pathname.startsWith(prefix))) {
    if (!user || ROLE_ORDER.indexOf(user.role) < ROLE_ORDER.indexOf('LID')) {
      return redirectTo('/auth/signin');
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/dashboard/:path*', '/notificaties', '/dashboard/profiel']
};

export type Role = 'GAST' | 'LID' | 'MOSKEE_BEHEERDER' | 'BEHEERDER';
export type Scope = 'own' | 'any' | 'platform';
export type Capability =
  | 'content.view_public'
  | 'content.view_members'
  | 'profile.manage'
  | 'events.register'
  | 'funeral.submit'
  | 'donations.use'
  | 'mosque.manage'
  | 'prayers.approve'
  | 'events.manage'
  | 'campaigns.manage'
  | 'payments.configure'
  | 'notifications.manage'
  | 'news.publish'
  | 'times.edit'
  | 'photos.upload'
  | 'analytics.view_mosque'
  | 'analytics.view_platform'
  | 'events.approve'
  | 'campaigns.approve'
  | 'users.manage'
  | 'roles.manage'
  | 'site.admin'
  | 'audit.view'
  | 'gdpr.process'
  | 'content.moderate'
  | 'payments.configure_platform';

export type Grant = `${Capability}` | `${Capability}:${Scope}`;

export interface RbacConfig {
  roles: Record<Role, { extends: Role[]; grants: Grant[] }>;
}

export interface AuthUser {
  id: string;
  role: Role;
  emailVerified: boolean;
  twoFAEnabled: boolean;
  managedMosqueIds?: string[];
}

import rawConfig from '../../../../config/rbac.config.json';
import type { RbacConfig, Role } from './types';

export const RBAC = rawConfig as unknown as RbacConfig;

export const ROLE_ORDER: Role[] = ['GAST', 'LID', 'MOSKEE_BEHEERDER', 'BEHEERDER'];

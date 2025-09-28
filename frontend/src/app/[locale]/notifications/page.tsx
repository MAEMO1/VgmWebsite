'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { NotificationsPage } from '@/components/notifications/NotificationBell';
import { Protected } from '@/app/components/Protected';

export default function NotificationsPageRoute() {
  const { user } = useAuth();
  
  return (
    <Protected 
      user={user} 
      capability="content.view_members"
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
            <p className="text-gray-600">You need to be logged in to view notifications.</p>
          </div>
        </div>
      }
    >
      <NotificationsPage />
    </Protected>
  );
}

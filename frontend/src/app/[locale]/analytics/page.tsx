'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/api/client';

interface AnalyticsSummary {
  page_views: Array<{ page_path: string; views: number }>;
  events: Array<{ event_type: string; count: number }>;
  user_activity: Array<{ activity_type: string; count: number }>;
  daily_stats: Array<{ date: string; page_views: number }>;
}

interface OverviewReport {
  total_users: number;
  total_mosques: number;
  total_events: number;
  total_donations: number;
  total_page_views: number;
  period_days: number;
}

interface UserReport {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  activity_count: number;
  last_activity: string;
}

interface MosqueReport {
  id: number;
  name: string;
  address: string;
  event_count: number;
  donation_count: number;
  analytics_events: number;
}

function AnalyticsDashboardContent() {
  const t = useTranslations('Analytics');
  const { user, isAdmin } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [overview, setOverview] = useState<OverviewReport | null>(null);
  const [users, setUsers] = useState<UserReport[]>([]);
  const [mosques, setMosques] = useState<MosqueReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'mosques' | 'summary'>('overview');
  const [days, setDays] = useState(30);

  useEffect(() => {
    if (isAdmin) {
      loadAnalytics();
    }
  }, [isAdmin, days, loadAnalytics]);

  const loadAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      
      // Load overview report
      const overviewResponse = await apiClient.get<OverviewReport>(`/api/analytics/reports?type=overview&days=${days}`);
      setOverview(overviewResponse);
      
      // Load user report
      const usersResponse = await apiClient.get<UserReport[]>(`/api/analytics/reports?type=users&days=${days}`);
      setUsers(usersResponse);
      
      // Load mosque report
      const mosquesResponse = await apiClient.get<MosqueReport[]>(`/api/analytics/reports?type=mosques&days=${days}`);
      setMosques(mosquesResponse);
      
      // Load summary
      const summaryResponse = await apiClient.get<AnalyticsSummary>(`/api/analytics/summary?days=${days}`);
      setSummary(summaryResponse);
      
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [days]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-BE');
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('nl-BE').format(num);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600 mb-4">
            Welcome back, {user?.first_name}! Here&apos;s what&apos;s happening with your website.
          </p>
          
          {/* Time Period Selector */}
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Time Period:</label>
            <select
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { key: 'overview', label: 'Overview', icon: '📊' },
                { key: 'users', label: 'Users', icon: '👥' },
                { key: 'mosques', label: 'Mosques', icon: '🕌' },
                { key: 'summary', label: 'Summary', icon: '📈' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && overview && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-blue-600">👥</div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Users</p>
                    <p className="text-2xl font-semibold text-gray-900">{formatNumber(overview.total_users)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-green-600">🕌</div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Active Mosques</p>
                    <p className="text-2xl font-semibold text-gray-900">{formatNumber(overview.total_mosques)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-purple-600">📅</div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Events</p>
                    <p className="text-2xl font-semibold text-gray-900">{formatNumber(overview.total_events)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-yellow-600">💰</div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Donations</p>
                    <p className="text-2xl font-semibold text-gray-900">{formatNumber(overview.total_donations)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="text-2xl text-red-600">👁️</div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Page Views</p>
                    <p className="text-2xl font-semibold text-gray-900">{formatNumber(overview.total_page_views)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
              </div>
              <div className="p-6">
                <p className="text-gray-600">Analytics data for the last {overview.period_days} days</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">User Activity Report</h2>
              <p className="text-sm text-gray-600 mt-1">User activity for the last {days} days</p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Activity Count</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {user.first_name} {user.last_name}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(user.activity_count)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.last_activity ? formatDate(user.last_activity) : 'Never'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'mosques' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Mosque Activity Report</h2>
              <p className="text-sm text-gray-600 mt-1">Mosque activity for the last {days} days</p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mosque</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Events</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Donations</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Analytics Events</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mosques.map((mosque) => (
                    <tr key={mosque.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{mosque.name}</div>
                          <div className="text-sm text-gray-500">{mosque.address}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(mosque.event_count)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(mosque.donation_count)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(mosque.analytics_events)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'summary' && summary && (
          <div className="space-y-6">
            {/* Page Views */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Top Pages</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {summary.page_views.map((page, index) => (
                    <div key={page.page_path} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-500 mr-4">#{index + 1}</span>
                        <span className="text-sm text-gray-900">{page.page_path}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{formatNumber(page.views)} views</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Event Types */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Event Types</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {summary.events.map((event, index) => (
                    <div key={event.event_type} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-500 mr-4">#{index + 1}</span>
                        <span className="text-sm text-gray-900">{event.event_type}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{formatNumber(event.count)} events</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Daily Stats */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Daily Page Views</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {summary.daily_stats.slice(0, 10).map((day, index) => (
                    <div key={day.date} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-500 mr-4">#{index + 1}</span>
                        <span className="text-sm text-gray-900">{formatDate(day.date)}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{formatNumber(day.page_views)} views</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function AnalyticsDashboardPage() {
  const { user, isAdmin } = useAuth();
  
  if (!user || !isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }
  
  return <AnalyticsDashboardContent />;
}

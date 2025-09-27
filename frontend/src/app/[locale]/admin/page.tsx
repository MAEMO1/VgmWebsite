'use client';

import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import { apiClient, MosqueAccessRequest } from '@/api/client';
import MosqueAccessModal from '@/components/admin/MosqueAccessModal';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  mosque_name?: string;
  created_at: string;
  is_active: boolean;
}

interface Event {
  id: number;
  title: string;
  description: string;
  event_date: string;
  event_time: string;
  mosque_name: string;
  created_by: number;
}

interface News {
  id: number;
  title: string;
  content: string;
  published_at: string;
  author_id: number;
}

interface Mosque {
  id: number;
  name: string;
  address: string;
  phone?: string;
  email?: string;
  website?: string;
  capacity?: number;
  established_year?: number;
  description?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at: string;
}

function AdminDashboard() {
  const { user, logout } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [news, setNews] = useState<News[]>([]);
  const [accessRequests, setAccessRequests] = useState<MosqueAccessRequest[]>([]);
  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [modalState, setModalState] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
    requestId: number;
    currentMosqueId?: number;
  }>({
    isOpen: false,
    type: 'approve',
    requestId: 0
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Load users
      const usersResponse = await apiClient.get<User[]>('/api/admin/users');
      setUsers(usersResponse);
      
      // Load events
      const eventsResponse = await apiClient.get<Event[]>('/api/events');
      setEvents(eventsResponse);
      
      // Load news
      const newsResponse = await apiClient.get<News[]>('/api/news');
      setNews(newsResponse);

      if (user?.role === 'admin') {
        const [requestsResponse, mosquesResponse] = await Promise.all([
          apiClient.getMosqueAccessRequests(),
          apiClient.get<Mosque[]>('/api/mosques')
        ]);
        setAccessRequests(requestsResponse);
        setMosques(mosquesResponse);
      } else {
        setAccessRequests([]);
        setMosques([]);
      }
      
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load admin data.');
    } finally {
      setLoading(false);
    }
  }, [user?.role]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAccessRequestUpdate = async (
    requestId: number,
    status: 'approved' | 'rejected',
    mosqueId?: number,
    adminNotes?: string
  ) => {
    try {
      const response = await apiClient.updateMosqueAccessRequest(requestId, {
        status,
        mosque_id: mosqueId,
        admin_notes: adminNotes,
      });

      toast.success(
        status === 'approved'
          ? 'Request approved and user promoted to mosque admin.'
          : 'Request rejected.'
      );

      setAccessRequests((prev) =>
        prev.map((request) => (request.id === requestId ? response.request : request))
      );

      // Refresh other data such as user list to reflect new roles
      loadData();
    } catch (error) {
      console.error('Failed to update access request', error);
      toast.error('Unable to update access request.');
    }
  };

  const openModal = (type: 'approve' | 'reject', requestId: number, currentMosqueId?: number) => {
    setModalState({
      isOpen: true,
      type,
      requestId,
      currentMosqueId
    });
  };

  const closeModal = () => {
    setModalState({
      isOpen: false,
      type: 'approve',
      requestId: 0
    });
  };

  const handleLogout = () => {
    logout();
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
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user?.first_name}!</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Role: {user?.role}</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'users', name: 'Users' },
              { id: 'events', name: 'Events' },
              { id: 'news', name: 'News' },
              ...(user?.role === 'admin'
                ? [{ id: 'accessRequests', name: 'Mosque Access Requests' }]
                : []),
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">U</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                        <dd className="text-lg font-medium text-gray-900">{users.length}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">E</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Events</dt>
                        <dd className="text-lg font-medium text-gray-900">{events.length}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                        <span className="text-white text-sm font-medium">N</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">News Articles</dt>
                        <dd className="text-lg font-medium text-gray-900">{news.length}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {user?.role === 'admin' && (
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Moskee Toegangsaanvragen</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Beheer aanvragen voor moskee-beheerder toegang
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-500">
                      {accessRequests.filter(r => r.status === 'pending').length} wachtend
                    </span>
                    <Link
                      href={`/${locale}/mosques/access-request`}
                      className="inline-flex items-center px-4 py-2 text-sm font-medium text-teal-600 bg-teal-50 border border-teal-200 rounded-lg hover:bg-teal-100 hover:border-teal-300 transition-colors"
                    >
                      <span>Nieuwe aanvraag</span>
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Users</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">Manage all registered users</p>
            </div>
            <ul className="divide-y divide-gray-200">
              {users.map((user) => (
                <li key={user.id}>
                  <div className="px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-700">
                            {user.first_name[0]}{user.last_name[0]}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.role === 'admin' ? 'bg-red-100 text-red-800' :
                        user.role === 'mosque_admin' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {user.role}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Events</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">Manage all events</p>
            </div>
            <ul className="divide-y divide-gray-200">
              {events.map((event) => (
                <li key={event.id}>
                  <div className="px-4 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{event.title}</h4>
                        <p className="text-sm text-gray-500">{event.description}</p>
                        <p className="text-sm text-gray-500">
                          {event.event_date} at {event.event_time} - {event.mosque_name}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-900 text-sm">Edit</button>
                        <button className="text-red-600 hover:text-red-900 text-sm">Delete</button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'news' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">News Articles</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">Manage all news articles</p>
            </div>
            <ul className="divide-y divide-gray-200">
              {news.map((article) => (
                <li key={article.id}>
                  <div className="px-4 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{article.title}</h4>
                        <p className="text-sm text-gray-500">
                          Published: {new Date(article.published_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-900 text-sm">Edit</button>
                        <button className="text-red-600 hover:text-red-900 text-sm">Delete</button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'accessRequests' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Mosque Access Requests</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Review and manage administrator access requests submitted by community members.
              </p>
            </div>
            <ul className="divide-y divide-gray-200">
              {accessRequests.length === 0 ? (
                <li className="px-4 py-4 text-sm text-gray-500">No requests found.</li>
              ) : (
                accessRequests.map((request) => (
                  <li key={request.id} className="px-4 py-4 sm:px-6">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">
                          {request.requester?.first_name} {request.requester?.last_name}
                        </p>
                        <p className="text-sm text-gray-600">{request.requester?.email}</p>
                        <p className="mt-2 text-sm text-gray-700">
                          <span className="font-medium">Mosque:</span>{' '}
                          {request.mosque?.name || request.mosque_name || 'Not specified'}
                        </p>
                        {request.motivation && (
                          <p className="mt-2 text-sm text-gray-600">
                            <span className="font-medium">Motivation:</span> {request.motivation}
                          </p>
                        )}
                        <p className="mt-2 text-xs text-gray-500">
                          Submitted{' '}
                          {request.created_at ? new Date(request.created_at).toLocaleString() : ''}
                        </p>
                        {request.admin_notes && (
                          <p className="mt-2 text-xs text-gray-500">Admin notes: {request.admin_notes}</p>
                        )}
                      </div>
                      <div className="flex flex-col items-start gap-2 md:items-end">
                        <span
                          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
                            request.status === 'approved'
                              ? 'bg-green-100 text-green-800'
                              : request.status === 'rejected'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {request.status.toUpperCase()}
                        </span>
                        {request.status === 'pending' && (
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => openModal('approve', request.id, request.mosque_id)}
                              className="rounded-md bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => openModal('reject', request.id)}
                              className="rounded-md bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700"
                            >
                              Reject
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </main>

      <MosqueAccessModal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onSubmit={(data) => handleAccessRequestUpdate(modalState.requestId, modalState.type, data.mosqueId, data.adminNotes)}
        type={modalState.type}
        currentMosqueId={modalState.currentMosqueId}
        mosques={mosques}
      />
    </div>
  );
}

export default withAuth(AdminDashboard, 'admin');

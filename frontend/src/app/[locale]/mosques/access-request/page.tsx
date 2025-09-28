'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import Link from 'next/link';
import toast from 'react-hot-toast';

import { apiClient, MosqueAccessRequest } from '@/api/client';
import type { Mosque } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';
import { Protected } from '@/app/components/Protected';

interface FormState {
  mosque_id: string;
  mosque_name: string;
  contact_email: string;
  contact_phone: string;
  motivation: string;
}

function MosqueAccessRequestPageContent() {
  const { isAuthenticated, user } = useAuth();
  const t = useTranslations('MosqueAccessRequest');
  const shared = useTranslations('Auth.Shared');
  const locale = useLocale();

  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [requests, setRequests] = useState<MosqueAccessRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<FormState>({
    mosque_id: '',
    mosque_name: '',
    contact_email: '',
    contact_phone: '',
    motivation: '',
  });

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        const [mosqueResponse, requestResponse] = await Promise.all([
          apiClient.getMosques(),
          apiClient.getMyMosqueAccessRequests(),
        ]);
        setMosques((mosqueResponse || []) as Mosque[]);
        setRequests(requestResponse);
        setForm((prev) => ({
          ...prev,
          contact_email: user?.email ?? prev.contact_email,
          contact_phone: user?.phone ?? prev.contact_phone,
        }));
      } catch (error) {
        console.error('Failed to load access request data', error);
        toast.error(t('errors.load'));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isAuthenticated, t, user?.email, user?.phone]);

  const hasPendingRequest = useMemo(
    () => requests.some((request) => request.status === 'pending'),
    [requests]
  );

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (hasPendingRequest) {
      toast.error(t('errors.pending'));
      return;
    }

    try {
      setSubmitting(true);
      const response = await apiClient.submitMosqueAccessRequest({
        mosque_id: form.mosque_id ? Number(form.mosque_id) : undefined,
        mosque_name: form.mosque_name || undefined,
        motivation: form.motivation || undefined,
        contact_email: form.contact_email || undefined,
        contact_phone: form.contact_phone || undefined,
      });

      toast.success(t('success'));
      setRequests((prev) => [response.request, ...prev]);
      setForm((prev) => ({
        ...prev,
        mosque_id: '',
        mosque_name: '',
        motivation: '',
      }));
    } catch (error) {
      console.error('Failed to submit access request', error);
      toast.error(t('errors.submit'));
    } finally {
      setSubmitting(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-semibold text-gray-900">{t('authRequired.title')}</h1>
          <p className="mt-3 text-sm text-gray-600">
            {t.rich('authRequired.description', {
              link: (chunks) => (
                <Link href={`/${locale}/login`} className="font-medium text-primary hover:text-primary-dark">
                  {chunks}
                </Link>
              ),
            })}
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-16 w-16 animate-spin rounded-full border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 lg:flex-row">
        <section className="mx-auto w-full max-w-3xl rounded-2xl border border-gray-100 bg-white p-8 shadow-sm lg:p-10">
          <h1 className="text-3xl font-semibold text-gray-900">{t('title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('subtitle')}</p>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-5">
              <div>
                <label htmlFor="mosque_id" className="block text-sm font-medium text-gray-700">
                  {t('form.existingMosqueLabel')}
                </label>
                <select
                  id="mosque_id"
                  name="mosque_id"
                  value={form.mosque_id}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">{t('form.existingMosquePlaceholder')}</option>
                  {mosques.map((mosque) => (
                    <option key={mosque.id} value={mosque.id.toString()}>
                      {mosque.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="mosque_name" className="block text-sm font-medium text-gray-700">
                  {t('form.newMosqueLabel')}
                </label>
                <input
                  id="mosque_name"
                  name="mosque_name"
                  type="text"
                  value={form.mosque_name}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={t('form.newMosquePlaceholder')}
                />
                <p className="mt-2 text-xs text-gray-500">{t('form.newMosqueHelper')}</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">
                    {shared('email')}
                  </label>
                  <input
                    id="contact_email"
                    name="contact_email"
                    type="email"
                    value={form.contact_email}
                    onChange={handleChange}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder={t('form.contactEmailPlaceholder')}
                  />
                </div>
                <div>
                  <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700">
                    {t('form.contactPhoneLabel')}
                  </label>
                  <input
                    id="contact_phone"
                    name="contact_phone"
                    type="tel"
                    value={form.contact_phone}
                    onChange={handleChange}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder={t('form.contactPhonePlaceholder')}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="motivation" className="block text-sm font-medium text-gray-700">
                  {t('form.motivationLabel')}
                </label>
                <textarea
                  id="motivation"
                  name="motivation"
                  value={form.motivation}
                  onChange={handleChange}
                  rows={5}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={t('form.motivationPlaceholder')}
                />
                <p className="mt-2 text-xs text-gray-500">{t('form.motivationHelper')}</p>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? (
                <>
                  <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  {t('form.submitBusy')}
                </>
              ) : (
                t('form.submit')
              )}
            </button>
          </form>
        </section>

        <aside className="mx-auto max-w-2xl space-y-6 text-sm text-gray-700">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('tips.title')}</h2>
            <ul className="mt-3 space-y-2 text-gray-600">
              <li>• {t('tips.items.0')}</li>
              <li>• {t('tips.items.1')}</li>
              <li>• {t('tips.items.2')}</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('history.title')}</h2>
            {requests.length === 0 ? (
              <p className="mt-2 text-sm text-gray-600">{t('history.empty')}</p>
            ) : (
              <ul className="mt-4 space-y-4">
                {requests.map((request) => (
                  <li key={request.id} className="rounded-lg border border-gray-100 bg-gray-50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">
                          {request.mosque?.name || request.mosque_name || t('history.unknownMosque')}
                        </p>
                        <p className="text-xs text-gray-500">
                          {request.created_at ? new Date(request.created_at).toLocaleString() : ''}
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          request.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : request.status === 'rejected'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {t(`status.${request.status}`)}
                      </span>
                    </div>
                    {request.admin_notes && (
                      <p className="mt-3 text-xs text-gray-600">{request.admin_notes}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

export default function MosqueAccessRequestPage() {
  const { user } = useAuth();
  
  return (
    <Protected 
      user={user} 
      capability="profile.manage"
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
            <p className="text-gray-600">You need to be logged in to request mosque access.</p>
          </div>
        </div>
      }
    >
      <MosqueAccessRequestPageContent />
    </Protected>
  );
}

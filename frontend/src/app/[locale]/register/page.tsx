'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { apiClient } from '@/api/client';
import type { Mosque } from '@/types/api';
import { UserPlusIcon } from '@heroicons/react/24/outline';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    mosque_id: '',
    mosque_name: '',
    admin_motivation: ''
  });
  const [accountType, setAccountType] = useState<'user' | 'mosque_admin'>('user');
  const [mosques, setMosques] = useState<Mosque[]>([]);
  const [mosqueLoading, setMosqueLoading] = useState(false);
  const [mosqueError, setMosqueError] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('Auth.Register');
  const shared = useTranslations('Auth.Shared');

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  useEffect(() => {
    const fetchMosques = async () => {
      try {
        setMosqueLoading(true);
        const response = await apiClient.get<Mosque[]>('/api/mosques');
        setMosques(response);
        setMosqueError('');
      } catch (err) {
        console.error('Failed to load mosques', err);
        setMosqueError(t('errors.mosqueLoad'));
      } finally {
        setMosqueLoading(false);
      }
    };

    fetchMosques();
  }, [t]);

  useEffect(() => {
    if (accountType !== 'mosque_admin') {
      setFormData((prev) => ({
        ...prev,
        mosque_id: '',
        mosque_name: '',
        admin_motivation: '',
      }));
    }
  }, [accountType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError(shared('errors.passwordMismatch'));
      return;
    }

    if (formData.password.length < 6) {
      setError(shared('errors.passwordLength'));
      return;
    }

    if (accountType === 'mosque_admin' && !formData.mosque_id) {
      setError(t('errors.mosqueRequired'));
      return;
    }

    setLoading(true);

    try {
      const success = await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone || undefined,
        mosque_id: formData.mosque_id ? parseInt(formData.mosque_id, 10) : undefined,
        role: accountType,
        mosque_name: formData.mosque_name || undefined,
        admin_motivation: formData.admin_motivation || undefined,
      });
      
      if (success) {
        router.push(`/${locale}/login?message=${encodeURIComponent(t('success'))}`);
      } else {
        setError(shared('genericError'));
      }
    } catch (err) {
      setError(shared('genericError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserPlusIcon className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {t('title')}
            </h1>
            <p className="text-gray-600">
              {t('subtitle')}
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            {mosqueError && (
              <div className="rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-700">
                {mosqueError}
              </div>
            )}

            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  {t('accountType.label')}
                </label>
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <label className={`flex cursor-pointer flex-col rounded-lg border px-4 py-3 text-sm shadow-sm transition ${
                    accountType === 'user'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-gray-200 hover:border-primary/60'
                  }`}>
                    <span className="font-medium">{t('accountType.user.title')}</span>
                    <span className="mt-1 text-xs text-gray-600">
                      {t('accountType.user.description')}
                    </span>
                    <input
                      type="radio"
                      name="accountType"
                      value="user"
                      checked={accountType === 'user'}
                      onChange={() => setAccountType('user')}
                      className="sr-only"
                    />
                  </label>
                  <label className={`flex cursor-pointer flex-col rounded-lg border px-4 py-3 text-sm shadow-sm transition ${
                    accountType === 'mosque_admin'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-gray-200 hover:border-primary/60'
                  }`}>
                    <span className="font-medium">{t('accountType.mosqueAdmin.title')}</span>
                    <span className="mt-1 text-xs text-gray-600">
                      {t('accountType.mosqueAdmin.description')}
                    </span>
                    <input
                      type="radio"
                      name="accountType"
                      value="mosque_admin"
                      checked={accountType === 'mosque_admin'}
                      onChange={() => setAccountType('mosque_admin')}
                      className="sr-only"
                    />
                  </label>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                    {shared('firstName')}
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={handleChange}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    placeholder={shared('placeholders.firstName')}
                  />
                </div>

                <div>
                  <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                    {shared('lastName')}
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={handleChange}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    placeholder={shared('placeholders.lastName')}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  {shared('email')}
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.email')}
                />
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  {t('phone.label')}
                </label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('phone.placeholder')}
                />
              </div>

              <div>
                <label htmlFor="mosque_id" className="block text-sm font-medium text-gray-700">
                  {t('mosque.label')}
                </label>
                <select
                  id="mosque_id"
                  name="mosque_id"
                  value={formData.mosque_id}
                  onChange={handleChange}
                  disabled={accountType !== 'mosque_admin'}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-gray-100 disabled:text-gray-500"
                >
                  <option value="">
                    {accountType === 'mosque_admin'
                      ? mosqueLoading
                        ? t('mosque.loading')
                        : t('mosque.placeholder')
                      : t('mosque.notRequired')}
                  </option>
                  {mosques.map((mosque) => (
                    <option key={mosque.id} value={mosque.id.toString()}>
                      {mosque.name}
                    </option>
                  ))}
              </select>
              {accountType === 'mosque_admin' && (
                <p className="mt-2 text-xs text-gray-500">
                  {t.rich('mosque.help', {
                    contact: (chunks) => (
                      <Link
                        href={`/${locale}/contact`}
                        className="font-medium text-teal-600 hover:text-teal-700 transition-colors"
                      >
                        {chunks}
                      </Link>
                    ),
                  })}
                </p>
              )}
            </div>

            {accountType === 'mosque_admin' && (
              <>
                <div>
                  <label htmlFor="mosque_name" className="block text-sm font-medium text-gray-700">
                    {t('mosque.customLabel')}
                  </label>
                  <input
                    id="mosque_name"
                    name="mosque_name"
                    type="text"
                    value={formData.mosque_name}
                    onChange={handleChange}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    placeholder={t('mosque.customPlaceholder')}
                  />
                </div>

                <div>
                  <label htmlFor="admin_motivation" className="block text-sm font-medium text-gray-700">
                    {t('motivation.label')}
                  </label>
                  <textarea
                    id="admin_motivation"
                    name="admin_motivation"
                    value={formData.admin_motivation}
                    onChange={handleChange}
                    rows={4}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    placeholder={t('motivation.placeholder')}
                  />
                  <p className="mt-2 text-xs text-gray-500">{t('motivation.helper')}</p>
                </div>
              </>
            )}

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  {shared('password')}
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.password')}
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                  {t('confirmPassword.label')}
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('confirmPassword.placeholder')}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-teal-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  {t('actions.creating')}
                </>
              ) : (
                t('actions.create')
              )}
            </button>
          </form>
        </section>

        <aside className="mx-auto max-w-lg space-y-6 text-sm text-gray-700">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('support.title')}</h2>
            <ul className="mt-3 space-y-2 text-gray-600">
              <li>• {t('support.points.0')}</li>
              <li>• {t('support.points.1')}</li>
              <li>• {t('support.points.2')}</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('nextSteps.title')}</h2>
            <p className="mt-2 text-gray-600">{t('nextSteps.description')}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

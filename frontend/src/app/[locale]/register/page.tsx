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
        setMosqueError('Kon moskeeën niet laden');
      } finally {
        setMosqueLoading(false);
      }
    };

    if (accountType === 'mosque_admin') {
      fetchMosques();
    }
  }, [accountType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError(shared('passwordMismatch'));
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
        if (accountType === 'mosque_admin') {
          router.push(`/${locale}/login?message=${encodeURIComponent(t('successMosqueAdmin'))}&showAccessRequest=true`);
        } else {
          router.push(`/${locale}/login?message=${encodeURIComponent(t('successUser'))}`);
        }
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

            {/* Account Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                {t('accountType.label')}
              </label>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() => setAccountType('user')}
                  className={`rounded-lg border p-4 text-left transition-colors ${
                    accountType === 'user'
                      ? 'border-teal-500 bg-teal-50 text-teal-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  }`}
                >
                  <div className="font-medium">{t('accountType.user.title')}</div>
                  <div className="text-sm text-gray-500">{t('accountType.user.description')}</div>
                </button>
                <button
                  type="button"
                  onClick={() => setAccountType('mosque_admin')}
                  className={`rounded-lg border p-4 text-left transition-colors ${
                    accountType === 'mosque_admin'
                      ? 'border-teal-500 bg-teal-50 text-teal-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  }`}
                >
                  <div className="font-medium">{t('accountType.mosqueAdmin.title')}</div>
                  <div className="text-sm text-gray-500">{t('accountType.mosqueAdmin.description')}</div>
                </button>
              </div>
              <p className="mt-3 text-xs text-gray-500">
                {t.rich('accountType.cta', {
                  link: (chunks) => (
                    <Link
                      href={`/${locale}/mosques/access-request`}
                      className="font-medium text-primary hover:text-primary-dark"
                    >
                      {t('accountType.ctaLinkLabel')}
                    </Link>
                  ),
                })}
              </p>
            </div>

            {/* Basic Information */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                  {shared('firstName')}
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.firstName')}
                />
              </div>
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                  {shared('lastName')}
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.lastName')}
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
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
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                placeholder={t('placeholders.email')}
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                {t('phone.label')}
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                placeholder={t('phone.placeholder')}
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
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
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.password')}
                />
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  {shared('confirmPassword')}
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.confirmPassword')}
                />
              </div>
            </div>

            {/* Mosque Admin Specific Fields */}
            {accountType === 'mosque_admin' && (
              <>
                <div>
                  <label htmlFor="mosque_id" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('mosque.label')}
                  </label>
                  {mosqueLoading ? (
                    <div className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-3 text-gray-500">
                      {t('mosque.loading')}
                    </div>
                  ) : mosqueError ? (
                    <div className="w-full rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-red-600">
                      {mosqueError}
                    </div>
                  ) : (
                    <select
                      id="mosque_id"
                      name="mosque_id"
                      required
                      value={formData.mosque_id}
                      onChange={handleChange}
                      className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    >
                      <option value="">{t('mosque.placeholder')}</option>
                      {mosques.map((mosque) => (
                        <option key={mosque.id} value={mosque.id}>
                          {mosque.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div>
                  <label htmlFor="admin_motivation" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('motivation.label')}
                  </label>
                  <textarea
                    id="admin_motivation"
                    name="admin_motivation"
                    rows={3}
                    value={formData.admin_motivation}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                    placeholder={t('motivation.placeholder')}
                  />
                </div>

                <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                  <p className="text-sm text-blue-800">
                    {t('motivation.helper')}
                  </p>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-teal-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  {t('actions.creating')}
                </>
              ) : (
                t('actions.createAccount')
              )}
            </button>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                {t.rich('cta', {
                  login: (chunks) => (
                    <Link
                      href={`/${locale}/login`}
                      className="font-medium text-teal-600 hover:text-teal-700 transition-colors"
                    >
                      {chunks}
                    </Link>
                  ),
                })}
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

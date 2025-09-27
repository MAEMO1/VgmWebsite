'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { LockClosedIcon } from '@heroicons/react/24/outline';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('Auth.Login');
  const shared = useTranslations('Auth.Shared');
  const searchParams = useSearchParams();
  const successMessage = searchParams.get('message');
  const showAccessRequest = searchParams.get('showAccessRequest') === 'true';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(email, password, remember);
      
      if (success) {
        router.push(`/${locale}`);
      } else {
        setError(t('errors.invalidCredentials'));
      }
    } catch (err) {
      setError(shared('genericError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-md">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <LockClosedIcon className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {t('title')}
            </h1>
            <p className="text-gray-600">
              {t('subtitle')}
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {successMessage && (
              <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                {successMessage}
                {showAccessRequest && (
                  <div className="mt-3">
                    <Link
                      href={`/${locale}/mosques/access-request`}
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-teal-600 bg-teal-50 border border-teal-200 rounded-lg hover:bg-teal-100 hover:border-teal-300 transition-colors"
                    >
                      <span>Moskee toegangsaanvraag indienen</span>
                    </Link>
                  </div>
                )}
              </div>
            )}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-4">
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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.email')}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  {shared('password')}
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder={t('placeholders.password')}
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex cursor-pointer items-center gap-2 text-gray-700">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                />
                <span>{t('rememberMe')}</span>
              </label>

              <Link
                href={`/${locale}/forgot-password`}
                className="font-medium text-teal-600 hover:text-teal-700 transition-colors"
              >
                {t('forgotPassword')}
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-teal-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  {t('actions.signingIn')}
                </>
              ) : (
                t('actions.signIn')
              )}
            </button>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              {t.rich('cta', {
                create: (chunks) => (
                  <Link
                    href={`/${locale}/register`}
                    className="font-medium text-teal-600 hover:text-teal-700 transition-colors"
                  >
                    {chunks}
                  </Link>
                ),
              })}
            </p>
          </div>
        </form>

        <div className="mt-8 rounded-lg border border-gray-200 bg-gray-50 p-6">
          <h2 className="text-sm font-semibold text-gray-900">{t('support.title')}</h2>
          <p className="mt-2 text-sm text-gray-600">{t('support.description')}</p>
          <ul className="mt-3 space-y-2 text-sm text-gray-600">
            <li>• {t('support.tips.0')}</li>
            <li>• {t('support.tips.1')}</li>
            <li>• {t('support.tips.2')}</li>
          </ul>
          <p className="mt-4 text-sm text-gray-600">
            {t.rich('support.cta', {
              link: (chunks) => (
                <Link
                  href={`/${locale}/mosques/access-request`}
                  className="font-medium text-teal-600 hover:text-teal-700"
                >
                  {t('support.ctaLinkLabel')}
                </Link>
              ),
            })}
          </p>
        </div>
      </div>
    </div>
  </div>
  );
}

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
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-8 lg:flex-row">
        <section className="mx-auto w-full max-w-lg rounded-2xl border border-gray-100 bg-white p-8 shadow-sm lg:p-10">
          <div className="flex items-center justify-center rounded-full bg-primary/10 p-3 text-primary">
            <LockClosedIcon className="h-6 w-6" aria-hidden="true" />
          </div>
          <h1 className="mt-6 text-center text-3xl font-semibold text-gray-900">
            {t('title')}
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t.rich('cta', {
              create: (chunks) => (
                <Link
                  href={`/${locale}/register`}
                  className="font-medium text-primary hover:text-primary-dark"
                >
                  {chunks}
                </Link>
              ),
            })}
          </p>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {successMessage && (
              <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                {successMessage}
              </div>
            )}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-5">
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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={t('placeholders.email')}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
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
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
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
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span>{t('rememberMe')}</span>
              </label>

              <Link
                href={`/${locale}/forgot-password`}
                className="font-medium text-primary hover:text-primary-dark"
              >
                {t('forgotPassword')}
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
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

            <div className="rounded-lg bg-gray-50 px-4 py-3 text-xs text-gray-600">
              <p className="font-medium text-gray-700">{t('demo.title')}</p>
              <ul className="mt-2 space-y-1">
                <li>{t('demo.admin')}</li>
                <li>{t('demo.mosqueAdmin')}</li>
                <li>{t('demo.user')}</li>
              </ul>
            </div>
          </form>
        </section>

        <aside className="mx-auto max-w-lg space-y-6 text-sm text-gray-700">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('support.title')}</h2>
            <p className="mt-2 text-gray-600">{t('support.description')}</p>
            <ul className="mt-4 space-y-2 text-gray-600">
              <li>• {t('support.tips.0')}</li>
              <li>• {t('support.tips.1')}</li>
              <li>• {t('support.tips.2')}</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{t('security.title')}</h2>
            <p className="mt-2 text-gray-600">{t('security.description')}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

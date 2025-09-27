'use client';

import { useState } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { EnvelopeIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

import { apiClient } from '@/api/client';

export default function ForgotPasswordPage() {
  const t = useTranslations('Auth.ForgotPassword');
  const shared = useTranslations('Auth.Shared');
  const locale = useLocale();

  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [requestLoading, setRequestLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [debugToken, setDebugToken] = useState<string | null>(null);

  const handleRequestReset = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!email) {
      toast.error(t('errors.emailRequired'));
      return;
    }

    try {
      setRequestLoading(true);
      const response = await apiClient.requestPasswordReset(email);
      if (response.reset_token) {
        setDebugToken(response.reset_token);
      }
      toast.success(t('request.success'));
    } catch (error) {
      console.error('Password reset request failed', error);
      toast.error(t('errors.requestFailed'));
    } finally {
      setRequestLoading(false);
    }
  };

  const handleResetPassword = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token || !newPassword) {
      toast.error(t('errors.tokenAndPasswordRequired'));
      return;
    }

    try {
      setResetLoading(true);
      await apiClient.resetPassword(token, newPassword);
      toast.success(t('reset.success'));
      setToken('');
      setNewPassword('');
    } catch (error) {
      console.error('Password reset failed', error);
      toast.error(t('errors.resetFailed'));
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-4xl flex-col gap-8 lg:flex-row">
        <section className="mx-auto w-full max-w-2xl rounded-2xl border border-gray-100 bg-white p-8 shadow-sm lg:p-10">
          <div className="flex items-center justify-center rounded-full bg-primary/10 p-3 text-primary">
            <EnvelopeIcon className="h-6 w-6" aria-hidden="true" />
          </div>
          <h1 className="mt-6 text-center text-3xl font-semibold text-gray-900">
            {t('title')}
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">{t('subtitle')}</p>

          <div className="mt-8 space-y-6">
            <form onSubmit={handleRequestReset} className="rounded-2xl border border-gray-100 bg-gray-50 p-6">
              <h2 className="text-lg font-semibold text-gray-900">{t('request.title')}</h2>
              <p className="mt-2 text-sm text-gray-600">{t('request.description')}</p>
              <div className="mt-4">
                <label htmlFor="reset-email" className="block text-sm font-medium text-gray-700">
                  {shared('email')}
                </label>
                <input
                  id="reset-email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={t('request.placeholder')}
                />
              </div>
              <button
                type="submit"
                disabled={requestLoading}
                className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {requestLoading ? (
                  <>
                    <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    {t('request.submitBusy')}
                  </>
                ) : (
                  t('request.submit')
                )}
              </button>
              {debugToken && (
                <p className="mt-3 text-xs text-gray-500">
                  {t('request.tokenNotice')}{' '}
                  <span className="font-mono text-gray-700">{debugToken}</span>
                </p>
              )}
            </form>

            <form onSubmit={handleResetPassword} className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900">{t('reset.title')}</h2>
              <p className="mt-2 text-sm text-gray-600">{t('reset.description')}</p>

              <div className="mt-4 space-y-4">
                <div>
                  <label htmlFor="reset-token" className="block text-sm font-medium text-gray-700">
                    {t('reset.tokenLabel')}
                  </label>
                  <input
                    id="reset-token"
                    type="text"
                    value={token}
                    onChange={(event) => setToken(event.target.value)}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label htmlFor="new-password" className="block text-sm font-medium text-gray-700">
                    {t('reset.passwordLabel')}
                  </label>
                  <input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={resetLoading}
                className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {resetLoading ? (
                  <>
                    <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    {t('reset.submitBusy')}
                  </>
                ) : (
                  t('reset.submit')
                )}
              </button>
            </form>

            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-6">
              <h2 className="text-lg font-semibold text-gray-900">{t('steps.title')}</h2>
              <ol className="mt-4 space-y-3 text-sm text-gray-700">
                <li>1. {t('steps.items.0')}</li>
                <li>2. {t('steps.items.1')}</li>
                <li>3. {t('steps.items.2')}</li>
              </ol>
            </div>

            <div className="rounded-2xl border border-primary/20 bg-primary/5 p-6 text-sm text-gray-700">
              <p className="font-medium text-primary">{t('contact.title')}</p>
              <p className="mt-2">
                {t.rich('contact.description', {
                  email: (chunks) => (
                    <a
                      href="mailto:info@vgm-gent.be"
                      className="font-medium text-primary hover:text-primary-dark"
                    >
                      {chunks}
                    </a>
                  ),
                })}
              </p>
              <p className="mt-3 text-xs text-gray-600">{t('contact.note')}</p>
            </div>

            <p className="text-sm text-gray-600">
              {t.rich('backToLogin', {
                link: (chunks) => (
                  <Link
                    href={`/${locale}/login`}
                    className="font-medium text-primary hover:text-primary-dark"
                  >
                    {chunks}
                  </Link>
                ),
              })}
            </p>
          </div>
        </section>

        <aside className="mx-auto max-w-lg space-y-6 text-sm text-gray-700">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3 text-primary">
              <ShieldCheckIcon className="h-6 w-6" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-gray-900">{t('security.title')}</h2>
            </div>
            <ul className="mt-4 space-y-2 text-gray-600">
              <li>• {t('security.tips.0')}</li>
              <li>• {t('security.tips.1')}</li>
              <li>• {t('security.tips.2')}</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">{shared('supportTitle')}</h2>
            <p className="mt-2 text-gray-600">{t('support.description')}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

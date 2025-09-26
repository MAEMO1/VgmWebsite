import { setRequestLocale } from 'next-intl/server';
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  setRequestLocale(locale);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Inloggen op je account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Of{' '}
            <a
              href={`/${locale}/register`}
              className="font-medium text-teal-600 hover:text-teal-500"
            >
              maak een nieuw account aan
            </a>
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}

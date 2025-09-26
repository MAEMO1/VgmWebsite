import { setRequestLocale } from 'next-intl/server';
import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage({
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
            Maak een nieuw account aan
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Of{' '}
            <a
              href={`/${locale}/login`}
              className="font-medium text-teal-600 hover:text-teal-500"
            >
              log in op je bestaande account
            </a>
          </p>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
}

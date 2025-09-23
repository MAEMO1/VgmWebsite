import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { IftarMap } from '@/components/ramadan/IftarMap';

export default function RamadanPage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  // Enable static rendering
  setRequestLocale(locale);
  
  const t = useTranslations('RamadanPage');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {t('title')}
        </h1>
        <p className="text-lg text-gray-600">
          {t('description')}
        </p>
      </div>
      
      <IftarMap />
    </div>
  );
}

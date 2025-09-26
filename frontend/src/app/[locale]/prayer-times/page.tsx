import { setRequestLocale } from 'next-intl/server';
import { PrayerTimesPage } from '@/components/prayer-times/PrayerTimesPage';

export default function PrayerTimesPageRoute({
  params: { locale }
}: {
  params: { locale: string };
}) {
  setRequestLocale(locale);

  return <PrayerTimesPage />;
}
import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { Hero } from '@/components/home/Hero';
import { Features } from '@/components/home/Features';
import { Mosques } from '@/components/home/Mosques';
import { Events } from '@/components/home/Events';

export default function HomePage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  // Enable static rendering
  setRequestLocale(locale);
  
  const t = useTranslations('HomePage');

  return (
    <div className="space-y-16">
      <Hero />
      <Features />
      <Mosques />
      <Events />
    </div>
  );
}

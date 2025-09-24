import { setRequestLocale } from 'next-intl/server';
import { Hero } from '@/components/home/Hero';
import { NewsSection } from '@/components/home/NewsSection';
import { EventsSection } from '@/components/home/EventsSection';
import { MosquesSection } from '@/components/home/MosquesSection';
import { DonationsSection } from '@/components/home/DonationsSection';
import { QuickLinksSection } from '@/components/home/QuickLinksSection';

export default function HomePage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  // Enable static rendering
  setRequestLocale(locale);

  return (
    <div>
      <Hero />
      <NewsSection />
      <EventsSection />
      <MosquesSection />
      <DonationsSection />
      <QuickLinksSection />
    </div>
  );
}

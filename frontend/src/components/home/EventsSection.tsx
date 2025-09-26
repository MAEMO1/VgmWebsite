'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';
import { useEvents } from '@/hooks/useApi';
import { CalendarIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { SectionErrorBoundary } from '@/components/ErrorBoundary';
import { EventsSkeleton } from '@/components/ui/Skeleton';
import { CardImage } from '@/components/ui/LazyImage';

export function EventsSection() {
  const locale = useLocale();
  const t = useTranslations('Events');
  const { data: events, isLoading, error } = useEvents();

  return (
    <SectionErrorBoundary sectionName="Evenementen">
      <EventsSectionContent 
        locale={locale} 
        t={t} 
        events={events} 
        isLoading={isLoading} 
        error={error} 
      />
    </SectionErrorBoundary>
  );
}

function EventsSectionContent({ 
  locale, 
  t, 
  events, 
  isLoading, 
  error 
}: {
  locale: string;
  t: any;
  events: any;
  isLoading: boolean;
  error: any;
}) {

  if (isLoading) {
    return <EventsSkeleton />;
  }

  if (error) {
    return (
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h2>
            <p className="text-lg text-red-600">
              Er is een fout opgetreden bij het laden van de evenementen
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h2>
            <p className="text-lg text-gray-600">
              {t('subtitle')}
            </p>
          </div>

          {/* Empty State */}
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CalendarIcon className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Geen evenementen gepland</h3>
            <p className="text-gray-500 mb-6">
              Er zijn momenteel geen evenementen gepland. Nieuwe evenementen worden hier weergegeven zodra ze beschikbaar zijn.
            </p>
            <Link
              href={`/${locale}/events`}
              className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Alle evenementen bekijken
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {t('title')}
          </h2>
          <p className="text-lg text-gray-600">
            {t('subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {events.slice(0, 3).map((event: any) => (
            <div key={event.id} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              {/* Event Image */}
              <CardImage
                src="/images/event-placeholder.jpg"
                alt={event.title || 'Evenement'}
                width={300}
                height={200}
                className="w-full h-48 object-cover"
              />
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {event.title}
                </h3>
                
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {event.description}
                </p>
                
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex items-center">
                    <CalendarIcon className="w-4 h-4 mr-2" />
                    <span>{event.event_date ? new Date(event.event_date).toLocaleDateString('nl-NL') : 'TBD'}</span>
                  </div>
                  <div className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-2" />
                    <span>{event.event_time}</span>
                  </div>
                  {event.mosque_id && (
                    <div className="flex items-center">
                      <MapPinIcon className="w-4 h-4 mr-2" />
                      <span>Moskee ID: {event.mosque_id}</span>
                    </div>
                  )}
                </div>
                
                <Link
                  href={`/${locale}/events/${event.id}`}
                  className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Meer informatie
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href={`/${locale}/events`}
            className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Alle evenementen bekijken
          </Link>
        </div>
      </div>
    </div>
  );
}

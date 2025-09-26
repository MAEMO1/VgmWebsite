'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';
import { useNewsPosts } from '@/hooks/useApi';
import { NewspaperIcon, CalendarIcon, UserIcon } from '@heroicons/react/24/outline';
import { SectionErrorBoundary } from '@/components/ErrorBoundary';
import { NewsSkeleton } from '@/components/ui/Skeleton';

export function NewsSection() {
  const locale = useLocale();
  const t = useTranslations('News');
  const { data: newsPosts, isLoading, error } = useNewsPosts();

  return (
    <SectionErrorBoundary sectionName="Nieuws">
      <NewsSectionContent 
        locale={locale} 
        t={t} 
        newsPosts={newsPosts} 
        isLoading={isLoading} 
        error={error} 
      />
    </SectionErrorBoundary>
  );
}

function NewsSectionContent({ 
  locale, 
  t, 
  newsPosts, 
  isLoading, 
  error 
}: {
  locale: string;
  t: any;
  newsPosts: any;
  isLoading: boolean;
  error: any;
}) {

  if (isLoading) {
    return <NewsSkeleton />;
  }

  if (error) {
    return (
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h2>
            <p className="text-lg text-red-600">
              Er is een fout opgetreden bij het laden van het nieuws
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!newsPosts || newsPosts.length === 0) {
    return (
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t('title')}
            </h2>
            <p className="text-lg text-gray-600">
              Blijf op de hoogte van het laatste nieuws en aankondigingen
            </p>
          </div>

          {/* Empty State */}
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <NewspaperIcon className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Geen nieuws</h3>
            <p className="text-gray-500 mb-6">
              Er zijn momenteel geen nieuwsartikelen beschikbaar.
            </p>
            <Link
              href={`/${locale}/news`}
              className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Alle nieuws bekijken
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {t('title')}
          </h2>
          <p className="text-lg text-gray-600">
            Blijf op de hoogte van het laatste nieuws en aankondigingen
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {newsPosts.slice(0, 3).map((news: any) => (
            <div key={news.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition-shadow">
              {/* News Image Placeholder */}
              <div className="h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
                  <NewspaperIcon className="w-10 h-10 text-white" />
                </div>
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {news.title}
                </h3>
                
                <p className="text-gray-600 mb-4 line-clamp-3">
                  {news.excerpt || news.content?.substring(0, 150) + '...'}
                </p>
                
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  {news.published_at && (
                    <div className="flex items-center">
                      <CalendarIcon className="w-4 h-4 mr-2" />
                      <span>{new Date(news.published_at).toLocaleDateString('nl-NL')}</span>
                    </div>
                  )}
                  {news.author_id && (
                    <div className="flex items-center">
                      <UserIcon className="w-4 h-4 mr-2" />
                      <span>Author ID: {news.author_id}</span>
                    </div>
                  )}
                </div>
                
                <Link
                  href={`/${locale}/news/${news.id}`}
                  className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Lees meer
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href={`/${locale}/news`}
            className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Alle nieuws bekijken
          </Link>
        </div>
      </div>
    </div>
  );
}

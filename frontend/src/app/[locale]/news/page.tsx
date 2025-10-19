'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { CalendarIcon, UserIcon, TagIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/api/client';
import { ErrorState } from '@/components/ui/ErrorState';

interface NewsArticle {
  id: number;
  title: string;
  content: string;
  excerpt: string;
  author_id: number;
  first_name: string;
  last_name: string;
  category: string;
  featured_image: string;
  status: string;
  published_at: string;
  created_at: string;
  updated_at: string;
}

export default function NewsPage() {
  const t = useTranslations('News');
  const [activeTab, setActiveTab] = useState('overview');

  const { data: newsArticles = [], isLoading, isError } = useQuery<NewsArticle[]>({
    queryKey: ['news'],
    queryFn: () => apiClient.get<NewsArticle[]>('/api/news'),
    refetchOnWindowFocus: false,
  });

  const tabs = [
    { id: 'overview', name: 'Overzicht' },
    { id: 'news', name: 'Nieuws' },
    { id: 'announcements', name: 'Aankondigingen' },
    { id: 'reflections', name: 'Reflecties' }
  ];

  const filteredArticles = newsArticles.filter(article => {
    switch (activeTab) {
      case 'news':
        return article.category === 'news';
      case 'announcements':
        return article.category === 'announcement';
      case 'reflections':
        return article.category === 'reflection';
      default:
        return true;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white">
        <Breadcrumbs items={[
          { name: 'Gemeenschap', href: '/community' },
          { name: 'Nieuws' }
        ]} />
        
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" aria-label="Nieuws wordt geladen" />
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-white">
        <Breadcrumbs items={[
          { name: 'Gemeenschap', href: '/community' },
          { name: 'Nieuws' }
        ]} />
        
        <div className="max-w-6xl mx-auto px-6 py-8">
          <ErrorState
            title="Nieuws laden mislukt"
            message="Het laden van nieuwsartikelen is mislukt. Probeer het later opnieuw."
            tone="critical"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Breadcrumbs items={[
        { name: 'Gemeenschap', href: '/community' },
        { name: 'Nieuws' }
      ]} />
      
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Nieuws & Aankondigingen
          </h1>
          <p className="text-gray-600 text-lg">
            Blijf op de hoogte van het laatste nieuws en aankondigingen van de VGM.
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content based on active tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Latest News */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Laatste Nieuws</h2>
              {filteredArticles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredArticles.slice(0, 6).map((article) => (
                    <div key={article.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                      <div className="h-48 bg-gray-200"></div>
                      <div className="p-6">
                        <div className="flex items-center mb-2">
                          <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-blue-600 font-medium">{article.category}</span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{article.title}</h3>
                        <p className="text-gray-600 text-sm mb-4">{article.excerpt || 'Meer informatie volgt binnenkort.'}</p>
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <div className="flex items-center">
                            <UserIcon className="h-4 w-4 mr-1" />
                            {article.first_name} {article.last_name}
                          </div>
                          <div className="flex items-center">
                            <CalendarIcon className="h-4 w-4 mr-1" />
                            {new Date(article.published_at).toLocaleDateString('nl-NL')}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Geen nieuwsartikelen</h3>
                  <p className="text-gray-500">Er zijn momenteel geen nieuwsartikelen beschikbaar.</p>
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Snelle Acties</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors">
                  Alle Nieuws Bekijken
                </button>
                <button className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors">
                  Aankondigingen
                </button>
                <button className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors">
                  Reflecties
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'news' && (
          <div className="space-y-6">
            {filteredArticles.length > 0 ? (
              filteredArticles.map((article) => (
                <div key={article.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center mb-2">
                    <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-blue-600 font-medium">{article.category}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{article.title}</h3>
                  <p className="text-gray-600 mb-4">{article.excerpt || 'Meer informatie volgt binnenkort.'}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {article.first_name} {article.last_name}
                    </div>
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {new Date(article.published_at).toLocaleDateString('nl-NL')}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Geen nieuwsartikelen</h3>
                <p className="text-gray-500">Er zijn momenteel geen nieuwsartikelen beschikbaar.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'announcements' && (
          <div className="space-y-6">
            {filteredArticles.length > 0 ? (
              filteredArticles.map((article) => (
                <div key={article.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center mb-2">
                    <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-blue-600 font-medium">{article.category}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{article.title}</h3>
                  <p className="text-gray-600 mb-4">{article.excerpt || 'Meer informatie volgt binnenkort.'}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {article.first_name} {article.last_name}
                    </div>
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {new Date(article.published_at).toLocaleDateString('nl-NL')}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Geen aankondigingen</h3>
                <p className="text-gray-500">Er zijn momenteel geen aankondigingen beschikbaar.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'reflections' && (
          <div className="space-y-6">
            {filteredArticles.length > 0 ? (
              filteredArticles.map((article) => (
                <div key={article.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center mb-2">
                    <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-blue-600 font-medium">{article.category}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{article.title}</h3>
                  <p className="text-gray-600 mb-4">{article.excerpt || 'Meer informatie volgt binnenkort.'}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {article.first_name} {article.last_name}
                    </div>
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {new Date(article.published_at).toLocaleDateString('nl-NL')}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Geen reflecties</h3>
                <p className="text-gray-500">Er zijn momenteel geen reflecties beschikbaar.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

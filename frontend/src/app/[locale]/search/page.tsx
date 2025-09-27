'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import AdvancedSearch, { SearchResults } from '@/components/search/AdvancedSearch';
import type { Campaign, EventItem, Mosque, NewsArticle, SearchResult } from '@/types/api';

export default function SearchPage() {
  const t = useTranslations('Search');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleResults = (searchResults: SearchResult) => {
    setResults(searchResults);
  };

  const handleLoading = (isLoading: boolean) => {
    setLoading(isLoading);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleMosqueSelect = (mosque: Mosque) => {
    // Navigate to mosque details
    console.log('Selected mosque:', mosque);
  };

  const handleEventSelect = (event: EventItem) => {
    // Navigate to event details
    console.log('Selected event:', event);
  };

  const handleNewsSelect = (news: NewsArticle) => {
    // Navigate to news details
    console.log('Selected news:', news);
  };

  const handleCampaignSelect = (campaign: Campaign) => {
    // Navigate to campaign details
    console.log('Selected campaign:', campaign);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Advanced Search
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Search across mosques, events, news, and campaigns with advanced filters.
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Component */}
        <div className="mb-8">
          <AdvancedSearch
            onResults={handleResults}
            onLoading={handleLoading}
            onError={handleError}
          />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <SearchResults
            results={results}
            onMosqueSelect={handleMosqueSelect}
            onEventSelect={handleEventSelect}
            onNewsSelect={handleNewsSelect}
            onCampaignSelect={handleCampaignSelect}
          />
        )}

        {/* No Search Performed */}
        {!results && !loading && !error && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MagnifyingGlassIcon className="w-8 h-8 text-gray-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Start Your Search
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Use the search bar above to find mosques, events, news articles, and campaigns. 
              You can use advanced filters to narrow down your results by date, location, capacity, and more.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

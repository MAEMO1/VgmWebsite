'use client';

import React, { useState } from 'react';
import { apiClient } from '@/api/client';
import type { Campaign, EventItem, Mosque, NewsArticle, SearchResult } from '@/types/api';

interface SearchFilters {
  query: string;
  contentTypes: string[];
  dateFrom: string;
  dateTo: string;
  location: string;
  capacityMin: number | null;
  capacityMax: number | null;
  sortBy: string;
}

interface AdvancedSearchProps {
  onResults: (results: SearchResult) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string) => void;
}

export default function AdvancedSearch({ onResults, onLoading, onError }: AdvancedSearchProps) {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    contentTypes: ['mosques', 'events', 'news', 'campaigns'],
    dateFrom: '',
    dateTo: '',
    location: '',
    capacityMin: null,
    capacityMax: null,
    sortBy: 'relevance'
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    try {
      setSearching(true);
      onLoading(true);
      onError('');

      const params = new URLSearchParams();
      
      if (filters.query) params.append('q', filters.query);
      filters.contentTypes.forEach(type => params.append('type', type));
      if (filters.dateFrom) params.append('date_from', filters.dateFrom);
      if (filters.dateTo) params.append('date_to', filters.dateTo);
      if (filters.location) params.append('location', filters.location);
      if (filters.capacityMin) params.append('capacity_min', filters.capacityMin.toString());
      if (filters.capacityMax) params.append('capacity_max', filters.capacityMax.toString());
      params.append('sort', filters.sortBy);

      const response = await apiClient.get<SearchResult>(`/api/search?${params.toString()}`);
      onResults(response);

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Search failed';
      console.error('Search error:', error);
      onError(message);
    } finally {
      setSearching(false);
      onLoading(false);
    }
  };

  const handleFilterChange = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleContentTypeToggle = (type: string) => {
    setFilters(prev => ({
      ...prev,
      contentTypes: prev.contentTypes.includes(type)
        ? prev.contentTypes.filter(t => t !== type)
        : [...prev.contentTypes, type]
    }));
  };

  const clearFilters = () => {
    setFilters({
      query: '',
      contentTypes: ['mosques', 'events', 'news', 'campaigns'],
      dateFrom: '',
      dateTo: '',
      location: '',
      capacityMin: null,
      capacityMax: null,
      sortBy: 'relevance'
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="space-y-4">
        {/* Main Search Bar */}
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search mosques, events, news, campaigns..."
              value={filters.query}
              onChange={(e) => handleFilterChange('query', e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary text-lg"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={searching}
            className="bg-primary hover:bg-primary-dark text-white font-medium py-3 px-6 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Quick Filters */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
          
          <button
            onClick={clearFilters}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors"
          >
            Clear All
          </button>
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <div className="border-t pt-4 space-y-4">
            {/* Content Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Types
              </label>
              <div className="flex flex-wrap gap-2">
                {[
                  { key: 'mosques', label: '🕌 Mosques' },
                  { key: 'events', label: '📅 Events' },
                  { key: 'news', label: '📰 News' },
                  { key: 'campaigns', label: '💰 Campaigns' }
                ].map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => handleContentTypeToggle(key)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      filters.contentTypes.includes(key)
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  From Date
                </label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  To Date
                </label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <input
                type="text"
                placeholder="Enter city, address, or area..."
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>

            {/* Capacity Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Min Capacity
                </label>
                <input
                  type="number"
                  placeholder="e.g., 100"
                  value={filters.capacityMin || ''}
                  onChange={(e) => handleFilterChange('capacityMin', e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Capacity
                </label>
                <input
                  type="number"
                  placeholder="e.g., 500"
                  value={filters.capacityMax || ''}
                  onChange={(e) => handleFilterChange('capacityMax', e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
            </div>

            {/* Sort Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="relevance">Relevance</option>
                <option value="date">Date</option>
                <option value="name">Name</option>
                <option value="capacity">Capacity (Mosques only)</option>
              </select>
            </div>
          </div>
        )}

        {/* Search Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSearch}
            disabled={searching}
            className="bg-primary hover:bg-primary-dark text-white font-medium py-3 px-8 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Search Results Component
interface SearchResultsProps {
  results: SearchResult;
  onMosqueSelect?: (mosque: Mosque) => void;
  onEventSelect?: (event: EventItem) => void;
  onNewsSelect?: (news: NewsArticle) => void;
  onCampaignSelect?: (campaign: Campaign) => void;
}

export function SearchResults({ results, onMosqueSelect, onEventSelect, onNewsSelect, onCampaignSelect }: SearchResultsProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-BE');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('nl-BE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  if (results.total_results === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-6xl mb-4">🔍</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          No Results Found
        </h2>
        <p className="text-gray-600">
          Try adjusting your search criteria or filters.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Results Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Search Results
        </h2>
        <p className="text-gray-600">
          Found {results.total_results} results across all content types.
        </p>
      </div>

      {/* Mosques Results */}
      {results.mosques.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            🕌 Mosques ({results.mosques.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.mosques.map((mosque) => (
              <div
                key={mosque.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onMosqueSelect?.(mosque)}
              >
                <h4 className="font-semibold text-gray-900 mb-2">{mosque.name}</h4>
                <p className="text-sm text-gray-600 mb-2">{mosque.address}</p>
                {mosque.capacity && (
                  <p className="text-sm text-gray-500">Capacity: {mosque.capacity}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Events Results */}
      {results.events.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            📅 Events ({results.events.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.events.map((event) => (
              <div
                key={event.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onEventSelect?.(event)}
              >
                <h4 className="font-semibold text-gray-900 mb-2">{event.title}</h4>
                <p className="text-sm text-gray-600 mb-2">{event.mosque_name}</p>
                <p className="text-sm text-gray-500">
                  {formatDate(event.event_date)} at {event.event_time}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* News Results */}
      {results.news.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            📰 News ({results.news.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.news.map((news) => (
              <div
                key={news.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onNewsSelect?.(news)}
              >
                <h4 className="font-semibold text-gray-900 mb-2">{news.title}</h4>
                <p className="text-sm text-gray-600 mb-2">{news.excerpt}</p>
                <p className="text-sm text-gray-500">
                  By {news.first_name} {news.last_name} • {formatDate(news.published_at)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campaigns Results */}
      {results.campaigns.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            💰 Campaigns ({results.campaigns.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.campaigns.map((campaign) => (
              <div
                key={campaign.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onCampaignSelect?.(campaign)}
              >
                <h4 className="font-semibold text-gray-900 mb-2">{campaign.title}</h4>
                <p className="text-sm text-gray-600 mb-2">{campaign.mosque_name}</p>
                <p className="text-sm text-gray-500">
                  {formatCurrency(campaign.current_amount || 0)} / {formatCurrency(campaign.target_amount || 0)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

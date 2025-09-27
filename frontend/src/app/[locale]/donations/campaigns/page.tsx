'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { apiClient } from '@/api/client';
import DonationForm from '@/components/payments/DonationForm';

interface Campaign {
  id: number;
  title: string;
  description: string;
  target_amount: number;
  current_amount: number;
  progress_percentage: number;
  mosque_name: string;
  status: string;
  start_date: string;
  end_date: string;
  featured_image?: string;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [showDonationForm, setShowDonationForm] = useState(false);
  const [donationSuccess, setDonationSuccess] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<Campaign[]>('/api/campaigns');
      setCampaigns(response);
    } catch (error) {
      console.error('Error loading campaigns:', error);
      setError('Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  };

  const handleDonate = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    setShowDonationForm(true);
  };

  const handleDonationSuccess = (donationId: number) => {
    setDonationSuccess(true);
    setShowDonationForm(false);
    // Reload campaigns to update progress
    loadCampaigns();
  };

  const handleDonationError = (error: string) => {
    setError(error);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('nl-BE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-BE');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error && !donationSuccess) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => {
              setError('');
              loadCampaigns();
            }}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (donationSuccess) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <h1 className="text-2xl font-bold text-green-600 mb-4">Donation Successful!</h1>
          <p className="text-gray-600 mb-4">
            Thank you for your generous donation to {selectedCampaign?.title}.
          </p>
          <button
            onClick={() => {
              setDonationSuccess(false);
              setSelectedCampaign(null);
            }}
            className="btn btn-primary"
          >
            Back to Campaigns
          </button>
        </div>
      </div>
    );
  }

  if (showDonationForm && selectedCampaign) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="mb-8">
            <button
              onClick={() => setShowDonationForm(false)}
              className="text-primary hover:text-primary-dark mb-4"
            >
              ← Back to Campaigns
            </button>
            <h1 className="text-3xl font-bold text-gray-900">
              Donate to {selectedCampaign.title}
            </h1>
            <p className="text-gray-600 mt-2">{selectedCampaign.description}</p>
          </div>
          
          <DonationForm
            campaignId={selectedCampaign.id}
            mosqueId={selectedCampaign.mosque_name ? 1 : undefined}
            onSuccess={handleDonationSuccess}
            onError={handleDonationError}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Donation Campaigns
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Support our community through various donation campaigns. 
            Every contribution helps us maintain and improve our mosques and services.
          </p>
        </div>

        {campaigns.length === 0 ? (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Active Campaigns
            </h2>
            <p className="text-gray-600">
              There are currently no active donation campaigns.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                {campaign.featured_image && (
                  <div className="h-48 bg-gray-200">
                    <Image
                      src={campaign.featured_image}
                      alt={campaign.title}
                      width={400}
                      height={192}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                
                <div className="p-6">
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {campaign.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-2">
                      {campaign.mosque_name}
                    </p>
                    <p className="text-gray-700 text-sm line-clamp-3">
                      {campaign.description}
                    </p>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        Progress
                      </span>
                      <span className="text-sm font-medium text-gray-700">
                        {campaign.progress_percentage.toFixed(1)}%
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(campaign.progress_percentage, 100)}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex justify-between items-center text-sm text-gray-600">
                      <span>{formatCurrency(campaign.current_amount)}</span>
                      <span>{formatCurrency(campaign.target_amount)}</span>
                    </div>
                  </div>

                  <div className="mb-4 text-sm text-gray-600">
                    <p>Campaign Period:</p>
                    <p>
                      {formatDate(campaign.start_date)} - {formatDate(campaign.end_date)}
                    </p>
                  </div>

                  <button
                    onClick={() => handleDonate(campaign)}
                    className="w-full bg-primary hover:bg-primary-dark text-white font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    Donate Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* General Donation Section */}
        <div className="mt-16 bg-white rounded-lg shadow-md p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              General Donation
            </h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Make a general donation to support VGM&apos;s ongoing activities, 
              mosque maintenance, and community programs.
            </p>
            <button
              onClick={() => {
                setSelectedCampaign({
                  id: 0,
                  title: 'General Donation',
                  description: 'Support VGM&apos;s ongoing activities and community programs',
                  target_amount: 0,
                  current_amount: 0,
                  progress_percentage: 0,
                  mosque_name: '',
                  status: 'active',
                  start_date: new Date().toISOString(),
                  end_date: new Date().toISOString()
                });
                setShowDonationForm(true);
              }}
              className="bg-secondary hover:bg-secondary-dark text-white font-medium py-3 px-6 rounded-md transition-colors"
            >
              Make General Donation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { apiClient } from '@/api/client';

// Initialize Stripe
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_...');

interface PaymentFormProps {
  amount: number;
  donationType: string;
  mosqueId?: number;
  campaignId?: number;
  donorName?: string;
  donorEmail?: string;
  onSuccess: (donationId: number) => void;
  onError: (error: string) => void;
}

function PaymentForm({
  amount,
  donationType,
  mosqueId,
  campaignId,
  donorName,
  donorEmail,
  onSuccess,
  onError
}: PaymentFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [clientSecret, setClientSecret] = useState('');

  const createPaymentIntent = useCallback(async () => {
    try {
      const response = await apiClient.post<{
        client_secret: string;
        payment_intent_id: string;
      }>('/api/payments/create-payment-intent', {
        amount,
        donation_type: donationType,
        mosque_id: mosqueId,
        campaign_id: campaignId,
        donor_name: donorName,
        donor_email: donorEmail
      });

      setClientSecret(response.client_secret);
    } catch (error) {
      console.error('Error creating payment intent:', error);
      onError('Failed to initialize payment');
    }
  }, [amount, donationType, mosqueId, campaignId, donorName, donorEmail, onError]);

  useEffect(() => {
    // Create payment intent when component mounts
    createPaymentIntent();
  }, [amount, donationType, mosqueId, campaignId, createPaymentIntent]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements || !clientSecret) {
      return;
    }

    setLoading(true);

    try {
      const cardElement = elements.getElement(CardElement);
      
      if (!cardElement) {
        throw new Error('Card element not found');
      }

      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: donorName,
            email: donorEmail,
          },
        }
      });

      if (error) {
        onError(error.message || 'Payment failed');
      } else if (paymentIntent.status === 'succeeded') {
        // Confirm payment on backend
        const confirmResponse = await apiClient.post<{
          donation_id: number;
          status: string;
          amount: number;
          currency: string;
        }>('/api/payments/confirm-payment', {
          payment_intent_id: paymentIntent.id
        });

        onSuccess(confirmResponse.donation_id);
      }
    } catch (error) {
      console.error('Payment error:', error);
      onError('Payment processing failed');
    } finally {
      setLoading(false);
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Payment Information
        </h3>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Card Details
          </label>
          <div className="border border-gray-300 rounded-md p-3">
            <CardElement options={cardElementOptions} />
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-md">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Amount:</span>
            <span className="text-lg font-bold text-gray-900">
              €{amount.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between items-center mt-2">
            <span className="text-sm text-gray-600">Type:</span>
            <span className="text-sm text-gray-600 capitalize">
              {donationType.replace('_', ' ')}
            </span>
          </div>
        </div>

        <button
          type="submit"
          disabled={!stripe || loading}
          className="w-full mt-6 bg-primary hover:bg-primary-dark text-white font-medium py-3 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : `Donate €${amount.toFixed(2)}`}
        </button>
      </div>
    </form>
  );
}

interface DonationFormProps {
  mosqueId?: number;
  campaignId?: number;
  onSuccess: (donationId: number) => void;
  onError: (error: string) => void;
}

export default function DonationForm({ mosqueId, campaignId, onSuccess, onError }: DonationFormProps) {
  const [amount, setAmount] = useState(25);
  const [donationType, setDonationType] = useState('general');
  const [donorName, setDonorName] = useState('');
  const [donorEmail, setDonorEmail] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  const handleAmountSelect = (selectedAmount: number) => {
    setAmount(selectedAmount);
  };

  const handleCustomAmount = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(event.target.value);
    if (!isNaN(value) && value > 0) {
      setAmount(value);
    }
  };

  const handleDonationTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setDonationType(event.target.value);
  };

  const handleProceedToPayment = () => {
    if (!donorName.trim()) {
      onError('Please enter your name');
      return;
    }
    if (!donorEmail.trim()) {
      onError('Please enter your email');
      return;
    }
    setShowPaymentForm(true);
  };

  if (showPaymentForm) {
    return (
      <Elements stripe={stripePromise}>
        <PaymentForm
          amount={amount}
          donationType={donationType}
          mosqueId={mosqueId}
          campaignId={campaignId}
          donorName={donorName}
          donorEmail={donorEmail}
          onSuccess={onSuccess}
          onError={onError}
        />
      </Elements>
    );
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Make a Donation</h2>
      
      <div className="space-y-6">
        {/* Donation Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Donation Type
          </label>
          <select
            value={donationType}
            onChange={handleDonationTypeChange}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="general">General Donation</option>
            <option value="zakat">Zakat</option>
            <option value="sadaqah">Sadaqah</option>
            <option value="mosque_maintenance">Mosque Maintenance</option>
            <option value="education">Education</option>
            <option value="ramadan">Ramadan Activities</option>
          </select>
        </div>

        {/* Amount Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Amount
          </label>
          <div className="grid grid-cols-3 gap-2 mb-3">
            {[10, 25, 50, 100, 250, 500].map((presetAmount) => (
              <button
                key={presetAmount}
                type="button"
                onClick={() => handleAmountSelect(presetAmount)}
                className={`py-2 px-3 rounded-md text-sm font-medium ${
                  amount === presetAmount
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                €{presetAmount}
              </button>
            ))}
          </div>
          
          <div className="relative">
            <span className="absolute left-3 top-2 text-gray-500">€</span>
            <input
              type="number"
              min="1"
              step="0.01"
              value={amount}
              onChange={handleCustomAmount}
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Custom amount"
            />
          </div>
        </div>

        {/* Donor Information */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Name *
            </label>
            <input
              type="text"
              value={donorName}
              onChange={(e) => setDonorName(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Enter your full name"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              value={donorEmail}
              onChange={(e) => setDonorEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="Enter your email"
              required
            />
          </div>
        </div>

        {/* Proceed Button */}
        <button
          onClick={handleProceedToPayment}
          className="w-full bg-primary hover:bg-primary-dark text-white font-medium py-3 px-4 rounded-md"
        >
          Proceed to Payment - €{amount.toFixed(2)}
        </button>

        {/* Security Notice */}
        <div className="text-xs text-gray-500 text-center">
          <p>🔒 Your payment is secure and encrypted</p>
          <p>Powered by Stripe</p>
        </div>
      </div>
    </div>
  );
}

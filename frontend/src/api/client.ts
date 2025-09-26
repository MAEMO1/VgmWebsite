/**
 * API Client for VGM Website
 * Generated from OpenAPI schema with type safety
 */

import { paths, operations } from './types';

// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

// Request configuration
interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  body?: any;
  headers?: Record<string, string>;
}

// API Client class
class APIClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private csrfToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Set authentication token
  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Remove authentication token
  clearAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }

  // Get CSRF token from server
  private async getCSRFToken(): Promise<string> {
    if (this.csrfToken) {
      return this.csrfToken;
    }

    try {
      const response = await fetch(`${this.baseURL}/api/csrf`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        this.csrfToken = data.csrf_token || '';
        return this.csrfToken;
      }
    } catch (error) {
      console.warn('Failed to get CSRF token:', error);
    }

    return '';
  }

  // Clear CSRF token (call when logging out)
  clearCSRFToken() {
    this.csrfToken = null;
  }

  // Generic request method
  private async request<T>(config: RequestConfig): Promise<T> {
    const url = `${this.baseURL}${config.url}`;
    const headers = { ...this.defaultHeaders, ...config.headers };

    // Add CSRF token for state-changing requests
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method)) {
      const csrfToken = await this.getCSRFToken();
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }
    }

    try {
      const response = await fetch(url, {
        method: config.method,
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        credentials: 'include', // Include cookies for CSRF
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Auth endpoints
  async login(data: operations['loginUser']['requestBody']['content']['application/json']) {
    return this.request<operations['loginUser']['responses']['200']['content']['application/json']>({
      method: 'POST',
      url: '/api/auth/login',
      body: data,
    });
  }

  async register(data: operations['registerUser']['requestBody']['content']['application/json']) {
    return this.request<operations['registerUser']['responses']['201']['content']['application/json']>({
      method: 'POST',
      url: '/api/auth/register',
      body: data,
    });
  }

  async getCurrentUser() {
    return this.request<operations['getCurrentUser']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/auth/me',
    });
  }

  // Mosque endpoints
  async getMosques() {
    return this.request<operations['getMosques']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/mosques',
    });
  }

  async getMosque(mosqueId: number) {
    return this.request<operations['getMosque']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: `/api/mosques/${mosqueId}`,
    });
  }

  // Event endpoints
  async getEvents() {
    return this.request<operations['getEvents']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/events',
    });
  }

  async getEvent(eventId: number) {
    return this.request<operations['getEvent']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: `/api/events/${eventId}`,
    });
  }

  // Ramadan endpoints
  async getIftarEvents() {
    return this.request<operations['getIftarEvents']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/ramadan/iftar-events',
    });
  }

  // Donation endpoints
  async getDonations() {
    return this.request<operations['getDonations']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/donations',
    });
  }

  // News endpoints
  async getNews() {
    return this.request<operations['getNews']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: '/api/news',
    });
  }

  async getNewsArticle(newsId: number) {
    return this.request<operations['getNewsArticle']['responses']['200']['content']['application/json']>({
      method: 'GET',
      url: `/api/news/${newsId}`,
    });
  }
}

// Create singleton instance
export const apiClient = new APIClient();

// Export types for use in components
export type { paths, operations } from './types';

// Export specific types for common use
export type User = paths['/api/auth/me']['get']['responses']['200']['content']['application/json'];
export type Mosque = paths['/api/mosques/{mosque_id}']['get']['responses']['200']['content']['application/json'];
export type Event = paths['/api/events/{event_id}']['get']['responses']['200']['content']['application/json'];
export type IftarEvent = paths['/api/ramadan/iftar-events']['get']['responses']['200']['content']['application/json'][0];
export type Donation = paths['/api/donations']['get']['responses']['200']['content']['application/json'][0];
export type News = paths['/api/news/{news_id}']['get']['responses']['200']['content']['application/json'];

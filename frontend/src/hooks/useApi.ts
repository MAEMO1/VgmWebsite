/**
 * React Query hooks for VGM Website API
 * Provides type-safe data fetching with caching and error handling
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { User, Mosque, Event, IftarEvent, Donation, News } from '../api/client';

// Query keys for consistent caching
export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  mosques: {
    all: ['mosques'] as const,
    detail: (id: number) => ['mosques', id] as const,
  },
  events: {
    all: ['events'] as const,
    detail: (id: number) => ['events', id] as const,
  },
  ramadan: {
    iftarEvents: ['ramadan', 'iftar-events'] as const,
  },
  donations: {
    all: ['donations'] as const,
  },
  news: {
    all: ['news'] as const,
    detail: (id: number) => ['news', id] as const,
  },
} as const;

// Auth hooks
export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: () => apiClient.getCurrentUser(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { email: string; password: string; remember?: boolean }) =>
      apiClient.login(data),
    onSuccess: (data) => {
      // Set auth token if provided
      if ('token' in data && typeof data.token === 'string') {
        apiClient.setAuthToken(data.token);
      }
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: {
      email: string;
      password: string;
      first_name: string;
      last_name: string;
      phone?: string;
      role?: string;
      mosque_id?: number;
    }) => apiClient.register(data),
  });
}

// Mosque hooks
export function useMosques() {
  return useQuery({
    queryKey: queryKeys.mosques.all,
    queryFn: () => apiClient.getMosques(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useMosque(id: number) {
  return useQuery({
    queryKey: queryKeys.mosques.detail(id),
    queryFn: () => apiClient.getMosque(id),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!id,
  });
}

// Event hooks
export function useEvents() {
  return useQuery({
    queryKey: queryKeys.events.all,
    queryFn: () => apiClient.getEvents(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useEvent(id: number) {
  return useQuery({
    queryKey: queryKeys.events.detail(id),
    queryFn: () => apiClient.getEvent(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!id,
  });
}

// Ramadan hooks
export function useIftarEvents() {
  return useQuery({
    queryKey: queryKeys.ramadan.iftarEvents,
    queryFn: () => apiClient.getIftarEvents(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Donation hooks
export function useDonations() {
  return useQuery({
    queryKey: queryKeys.donations.all,
    queryFn: () => apiClient.getDonations(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// News hooks
export function useNews() {
  return useQuery({
    queryKey: queryKeys.news.all,
    queryFn: () => apiClient.getNews(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useNewsPosts() {
  return useQuery({
    queryKey: queryKeys.news.all,
    queryFn: () => apiClient.getNews(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useNewsArticle(id: number) {
  return useQuery({
    queryKey: queryKeys.news.detail(id),
    queryFn: () => apiClient.getNewsArticle(id),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!id,
  });
}

// Utility hooks
export function useLogout() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      // Clear auth token
      apiClient.clearAuthToken();
      // You might want to call a logout endpoint here
    },
    onSuccess: () => {
      // Clear all cached data
      queryClient.clear();
    },
  });
}

// Prefetch utilities
export function usePrefetchMosque() {
  const queryClient = useQueryClient();
  
  return (id: number) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.mosques.detail(id),
      queryFn: () => apiClient.getMosque(id),
      staleTime: 10 * 60 * 1000,
    });
  };
}

export function usePrefetchEvent() {
  const queryClient = useQueryClient();
  
  return (id: number) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.events.detail(id),
      queryFn: () => apiClient.getEvent(id),
      staleTime: 5 * 60 * 1000,
    });
  };
}

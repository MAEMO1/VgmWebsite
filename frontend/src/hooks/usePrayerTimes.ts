'use client';

import { useQuery } from '@tanstack/react-query';
import { getPrayerTimes, type PrayerTimes, type PrayerTimesResponse } from '@/lib/prayer-times';

export function usePrayerTimes(date?: Date) {
  return useQuery<PrayerTimesResponse>({
    queryKey: ['prayer-times', date?.toISOString().split('T')[0] || 'today'],
    queryFn: () => getPrayerTimes(date),
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    retry: 2,
    retryDelay: 5000,
  });
}

export function useTodayPrayerTimes() {
  return usePrayerTimes(new Date());
}

export function useTomorrowPrayerTimes() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return usePrayerTimes(tomorrow);
}

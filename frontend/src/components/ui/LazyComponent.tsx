'use client';

import { Suspense, lazy, ComponentType, useState, useEffect } from 'react';
import { Skeleton } from './Skeleton';

interface LazyComponentProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function LazyComponent({ children, fallback }: LazyComponentProps) {
  return (
    <Suspense fallback={fallback || <Skeleton className="w-full h-32" />}>
      {children}
    </Suspense>
  );
}

// Higher-order component for lazy loading
export function withLazyLoading<T extends object>(
  Component: ComponentType<T>,
  fallback?: React.ReactNode
) {
  return function LazyLoadedComponent(props: T) {
    return (
      <LazyComponent fallback={fallback}>
        <Component {...props} />
      </LazyComponent>
    );
  };
}

// Lazy load components with dynamic imports
export const LazyMosquesSection = lazy(() => 
  import('@/components/home/MosquesSection').then(module => ({ 
    default: module.MosquesSection 
  }))
);

export const LazyEventsSection = lazy(() => 
  import('@/components/home/EventsSection').then(module => ({ 
    default: module.EventsSection 
  }))
);

export const LazyNewsSection = lazy(() => 
  import('@/components/home/NewsSection').then(module => ({ 
    default: module.NewsSection 
  }))
);

export const LazyPrayerTimesWidget = lazy(() => 
  import('@/components/prayer-times/PrayerTimesWidget').then(module => ({ 
    default: module.PrayerTimesWidget 
  }))
);

// Preload critical components
export function preloadCriticalComponents() {
  if (typeof window !== 'undefined') {
    // Preload components that are likely to be needed
    import('@/components/home/MosquesSection');
    import('@/components/home/EventsSection');
    import('@/components/prayer-times/PrayerTimesWidget');
  }
}

// Intersection Observer hook for lazy loading
export function useIntersectionObserver(
  elementRef: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, options]);

  return isIntersecting;
}

// Performance optimization utilities

// Debounce function for search inputs and API calls
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Throttle function for scroll events and animations
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// Memoization for expensive calculations
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  keyGenerator?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>) => {
    const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

// Virtual scrolling helper
export function getVisibleRange(
  scrollTop: number,
  containerHeight: number,
  itemHeight: number,
  totalItems: number,
  overscan: number = 5
) {
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    totalItems - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  
  return { startIndex, endIndex };
}

// Image optimization helpers
export function getOptimizedImageUrl(
  src: string,
  width: number,
  height?: number,
  quality: number = 80
): string {
  // For external images, use a proxy service or return original
  if (src.startsWith('http')) {
    return src;
  }
  
  // For local images, Next.js will handle optimization
  return src;
}

// Bundle size optimization
export function preloadRoute(route: string) {
  if (typeof window !== 'undefined') {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = route;
    document.head.appendChild(link);
  }
}

// Critical resource hints
export function addResourceHints() {
  if (typeof window !== 'undefined') {
    // Preconnect to external domains
    const domains = [
      'https://fonts.googleapis.com',
      'https://fonts.gstatic.com',
      'https://ezanvakti.herokuapp.com',
    ];
    
    domains.forEach(domain => {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = domain;
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    });
  }
}

// Performance monitoring
export function measurePerformance(name: string, fn: () => void) {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const start = performance.now();
    fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
  } else {
    fn();
  }
}

// Web Vitals tracking
export function trackWebVitals() {
  if (typeof window !== 'undefined') {
    // Track Core Web Vitals
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(console.log);
      getFID(console.log);
      getFCP(console.log);
      getLCP(console.log);
      getTTFB(console.log);
    });
  }
}

// Service Worker registration for caching
export function registerServiceWorker() {
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then(registration => {
          console.log('SW registered: ', registration);
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
    });
  }
}

// Cache management
export class CacheManager {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  
  set(key: string, data: any, ttl: number = 300000) { // 5 minutes default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  clear() {
    this.cache.clear();
  }
  
  size() {
    return this.cache.size;
  }
}

// Global cache instance
export const globalCache = new CacheManager();

// Request deduplication
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();
  
  async deduplicate<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!;
    }
    
    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key);
    });
    
    this.pendingRequests.set(key, promise);
    return promise;
  }
}

export const requestDeduplicator = new RequestDeduplicator();

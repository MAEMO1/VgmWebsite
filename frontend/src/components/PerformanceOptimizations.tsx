'use client';

import { useEffect } from 'react';
import { addResourceHints, trackWebVitals, registerServiceWorker } from '@/lib/performance';

export function PerformanceOptimizations() {
  useEffect(() => {
    // Add resource hints for external domains
    addResourceHints();
    
    // Track Web Vitals in development
    if (process.env.NODE_ENV === 'development') {
      trackWebVitals();
    }
    
    // Register service worker for caching
    registerServiceWorker();
  }, []);

  return null;
}

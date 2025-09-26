'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { Skeleton } from './Skeleton';

interface LazyImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  className?: string;
  priority?: boolean;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  sizes?: string;
  quality?: number;
}

export function LazyImage({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  placeholder = 'blur',
  blurDataURL,
  sizes,
  quality = 75,
}: LazyImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (priority) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoaded(true);
  };

  // Generate a simple blur placeholder if none provided
  const defaultBlurDataURL = blurDataURL || `data:image/svg+xml;base64,${Buffer.from(
    `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f3f4f6"/>
      <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#9ca3af" font-size="14">Loading...</text>
    </svg>`
  ).toString('base64')}`;

  if (hasError) {
    return (
      <div
        ref={imgRef}
        className={`bg-gray-200 flex items-center justify-center ${className}`}
        style={{ width, height }}
      >
        <div className="text-center text-gray-500">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-xs">Image not available</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={imgRef} className={`relative ${className}`} style={{ width, height }}>
      {!isLoaded && (
        <Skeleton className="absolute inset-0" />
      )}
      
      {isInView && (
        <Image
          src={src}
          alt={alt}
          width={width}
          height={height}
          className={`transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={handleLoad}
          onError={handleError}
          priority={priority}
          placeholder={placeholder}
          blurDataURL={placeholder === 'blur' ? defaultBlurDataURL : undefined}
          sizes={sizes}
          quality={quality}
        />
      )}
    </div>
  );
}

// Optimized image component for different use cases
export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  ...props
}: LazyImageProps) {
  return (
    <LazyImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={priority}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      quality={85}
      {...props}
    />
  );
}

// Hero image component with priority loading
export function HeroImage({
  src,
  alt,
  width,
  height,
  className = '',
  ...props
}: LazyImageProps) {
  return (
    <LazyImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={true}
      sizes="100vw"
      quality={90}
      {...props}
    />
  );
}

// Card image component for listings
export function CardImage({
  src,
  alt,
  width = 300,
  height = 200,
  className = '',
  ...props
}: LazyImageProps) {
  return (
    <LazyImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={false}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      quality={80}
      {...props}
    />
  );
}

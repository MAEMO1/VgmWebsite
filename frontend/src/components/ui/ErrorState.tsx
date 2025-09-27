'use client';

import React from 'react';
import Link from 'next/link';

interface ErrorStateProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onRetry?: () => void;
  href?: string;
  tone?: 'neutral' | 'critical';
}

export function ErrorState({
  title = 'Er ging iets mis',
  message = 'We konden deze inhoud niet laden. Probeer het later opnieuw.',
  actionLabel,
  onRetry,
  href,
  tone = 'neutral'
}: ErrorStateProps) {
  const content = (
    <>
      <h3 className={`text-lg font-semibold ${tone === 'critical' ? 'text-red-600' : 'text-gray-900'} mb-2`}>
        {title}
      </h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {message}
      </p>
      {actionLabel && onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
        >
          {actionLabel}
        </button>
      )}
      {actionLabel && href && (
        <Link
          href={href}
          className="inline-flex items-center px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
        >
          {actionLabel}
        </Link>
      )}
    </>
  );

  return (
    <div className="py-16 bg-white">
      <div className="max-w-4xl mx-auto px-6 text-center">
        {content}
      </div>
    </div>
  );
}

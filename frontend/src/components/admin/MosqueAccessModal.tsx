'use client';

import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface MosqueAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { mosqueId?: number; adminNotes?: string }) => void;
  type: 'approve' | 'reject';
  currentMosqueId?: number;
  mosques: Array<{ id: number; name: string }>;
}

export default function MosqueAccessModal({
  isOpen,
  onClose,
  onSubmit,
  type,
  currentMosqueId,
  mosques
}: MosqueAccessModalProps) {
  const [mosqueId, setMosqueId] = useState<number | undefined>(currentMosqueId);
  const [adminNotes, setAdminNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onSubmit({
        mosqueId: type === 'approve' ? mosqueId : undefined,
        adminNotes: type === 'reject' ? adminNotes : undefined
      });
      onClose();
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setMosqueId(currentMosqueId);
    setAdminNotes('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-25" onClick={handleClose} />
        
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              {type === 'approve' ? 'Approve Mosque Access Request' : 'Reject Mosque Access Request'}
            </h3>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6">
            {type === 'approve' && (
              <div className="mb-4">
                <label htmlFor="mosqueId" className="block text-sm font-medium text-gray-700 mb-2">
                  Select Mosque
                </label>
                <select
                  id="mosqueId"
                  value={mosqueId || ''}
                  onChange={(e) => setMosqueId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                >
                  <option value="">Select a mosque</option>
                  {mosques.map((mosque) => (
                    <option key={mosque.id} value={mosque.id}>
                      {mosque.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  Choose the mosque this user will manage
                </p>
              </div>
            )}

            {type === 'reject' && (
              <div className="mb-4">
                <label htmlFor="adminNotes" className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Rejection (Optional)
                </label>
                <textarea
                  id="adminNotes"
                  rows={3}
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
                  placeholder="Provide a reason for rejection..."
                />
                <p className="mt-1 text-sm text-gray-500">
                  This will be sent to the user via email
                </p>
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || (type === 'approve' && !mosqueId)}
                className={`px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                  type === 'approve'
                    ? 'bg-teal-600 hover:bg-teal-700 focus:ring-teal-500'
                    : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                }`}
              >
                {loading ? (
                  <span className="inline-flex items-center">
                    <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2" />
                    Processing...
                  </span>
                ) : (
                  type === 'approve' ? 'Approve Request' : 'Reject Request'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

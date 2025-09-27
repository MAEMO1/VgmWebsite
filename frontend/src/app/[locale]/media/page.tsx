'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { apiClient } from '@/api/client';
import FileUpload, { FileList } from '@/components/upload/FileUpload';

interface MediaFile {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  mime_type: string;
  uploaded_by: number;
  mosque_id?: number;
  event_id?: number;
  campaign_id?: number;
  description?: string;
  is_public: boolean;
  created_at: string;
  first_name?: string;
  last_name?: string;
  mosque_name?: string;
}

export default function MediaGalleryPage() {
  const t = useTranslations('MediaGallery');
  const [files, setFiles] = useState<MediaFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<MediaFile[]>('/api/files');
      setFiles(response);
    } catch (error) {
      console.error('Error loading files:', error);
      setError('Failed to load media files');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (file: any) => {
    setUploadSuccess(true);
    setShowUploadForm(false);
    loadFiles(); // Reload files
    setTimeout(() => setUploadSuccess(false), 3000);
  };

  const handleUploadError = (error: string) => {
    setError(error);
    setTimeout(() => setError(''), 5000);
  };

  const handleDeleteFile = async (fileId: number) => {
    try {
      await apiClient.delete(`/api/files/${fileId}`);
      loadFiles(); // Reload files
    } catch (error) {
      console.error('Error deleting file:', error);
      setError('Failed to delete file');
    }
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.mosque_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || 
                       (filterType === 'images' && file.mime_type.startsWith('image/')) ||
                       (filterType === 'documents' && (file.mime_type.includes('pdf') || file.mime_type.includes('word') || file.mime_type.includes('excel'))) ||
                       (filterType === 'other' && !file.mime_type.startsWith('image/') && !file.mime_type.includes('pdf') && !file.mime_type.includes('word') && !file.mime_type.includes('excel'));
    
    return matchesSearch && matchesType;
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-BE');
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) return '🖼️';
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word')) return '📝';
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '📊';
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) return '📽️';
    return '📁';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Media Gallery
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Browse and manage uploaded media files for mosques, events, and campaigns.
            </p>
          </div>

          {/* Controls */}
          <div className="flex flex-col lg:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>

            {/* Type Filter */}
            <div className="lg:w-48">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              >
                <option value="all">All Types</option>
                <option value="images">Images</option>
                <option value="documents">Documents</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Upload Button */}
            <button
              onClick={() => setShowUploadForm(true)}
              className="bg-primary hover:bg-primary-dark text-white font-medium py-2 px-6 rounded-md transition-colors"
            >
              📤 Upload Files
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Success/Error Messages */}
        {uploadSuccess && (
          <div className="mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            File uploaded successfully!
          </div>
        )}
        
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Files Grid */}
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📁</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Files Found
            </h2>
            <p className="text-gray-600 mb-6">
              {searchTerm || filterType !== 'all' 
                ? 'Try adjusting your search criteria or filters.'
                : 'No files have been uploaded yet.'
              }
            </p>
            <button
              onClick={() => setShowUploadForm(true)}
              className="bg-primary hover:bg-primary-dark text-white font-medium py-3 px-6 rounded-md transition-colors"
            >
              Upload First File
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredFiles.map((file) => (
              <div key={file.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                {/* File Preview */}
                <div className="h-48 bg-gray-100 flex items-center justify-center">
                  {file.mime_type.startsWith('image/') ? (
                    <Image
                      src={`/api/files/${file.id}`}
                      alt={file.original_filename}
                      width={400}
                      height={192}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-6xl text-gray-400">
                      {getFileIcon(file.mime_type)}
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="p-4">
                  <h3 className="font-medium text-gray-900 mb-2 truncate">
                    {file.original_filename}
                  </h3>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>📏 {formatFileSize(file.file_size)}</p>
                    <p>📅 {formatDate(file.created_at)}</p>
                    {file.mosque_name && (
                      <p>🕌 {file.mosque_name}</p>
                    )}
                    {file.first_name && file.last_name && (
                      <p>👤 {file.first_name} {file.last_name}</p>
                    )}
                  </div>

                  {file.description && (
                    <p className="text-sm text-gray-700 mt-2 line-clamp-2">
                      {file.description}
                    </p>
                  )}

                  <div className="flex gap-2 mt-4">
                    <a
                      href={`/api/files/${file.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 bg-primary hover:bg-primary-dark text-white text-center font-medium py-2 px-3 rounded-md transition-colors"
                    >
                      View
                    </a>
                    <button
                      onClick={() => handleDeleteFile(file.id)}
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white text-center font-medium py-2 px-3 rounded-md transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Upload Files
                </h2>
                <button
                  onClick={() => setShowUploadForm(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <FileUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
                multiple={true}
                maxSize={16}
                allowedTypes={[
                  'image/*',
                  'application/pdf',
                  'text/*',
                  'application/msword',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'application/vnd.ms-excel',
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                  'application/vnd.ms-powerpoint',
                  'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                ]}
              />

              <div className="mt-6 flex gap-4">
                <button
                  onClick={() => setShowUploadForm(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-3 px-4 rounded-md transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

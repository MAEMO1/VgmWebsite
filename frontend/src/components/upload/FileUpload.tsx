'use client';

import React, { useState, useRef } from 'react';
import { apiClient } from '@/api/client';
import { 
  DocumentIcon, 
  PhotoIcon, 
  VideoCameraIcon,
  PresentationChartBarIcon,
  TableCellsIcon
} from '@heroicons/react/24/outline';

interface FileUploadProps {
  onUploadSuccess: (file: any) => void;
  onUploadError: (error: string) => void;
  mosqueId?: number;
  eventId?: number;
  campaignId?: number;
  maxSize?: number; // in MB
  allowedTypes?: string[];
  multiple?: boolean;
}

export default function FileUpload({
  onUploadSuccess,
  onUploadError,
  mosqueId,
  eventId,
  campaignId,
  maxSize = 16,
  allowedTypes = ['image/*', 'application/pdf', 'text/*', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  multiple = false
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files: FileList) => {
    const fileArray = Array.from(files);
    
    if (!multiple && fileArray.length > 1) {
      onUploadError('Only one file can be uploaded at a time');
      return;
    }

    for (const file of fileArray) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file: File) => {
    try {
      setUploading(true);
      setUploadProgress(0);

      // Validate file size
      if (file.size > maxSize * 1024 * 1024) {
        onUploadError(`File size must be less than ${maxSize}MB`);
        return;
      }

      // Validate file type
      const isValidType = allowedTypes.some(type => {
        if (type.endsWith('/*')) {
          return file.type.startsWith(type.slice(0, -1));
        }
        return file.type === type;
      });

      if (!isValidType) {
        onUploadError('File type not allowed');
        return;
      }

      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', file.name);
      
      if (mosqueId) formData.append('mosque_id', mosqueId.toString());
      if (eventId) formData.append('event_id', eventId.toString());
      if (campaignId) formData.append('campaign_id', campaignId.toString());
      formData.append('is_public', 'true');

      // Upload file
      const response = await apiClient.post('/api/upload', formData, {
        'Content-Type': 'multipart/form-data'
      });

      setUploadProgress(100);
      onUploadSuccess(response);
      
    } catch (error: any) {
      console.error('Upload error:', error);
      onUploadError(error.message || 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) return <PhotoIcon className="w-5 h-5" />;
    if (fileType.includes('pdf')) return <DocumentIcon className="w-5 h-5" />;
    if (fileType.includes('word')) return <DocumentIcon className="w-5 h-5" />;
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return <TableCellsIcon className="w-5 h-5" />;
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) return <PresentationChartBarIcon className="w-5 h-5" />;
    return <DocumentIcon className="w-5 h-5" />;
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-primary bg-primary/5'
            : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple={multiple}
          accept={allowedTypes.join(',')}
          onChange={handleFileInput}
          className="hidden"
        />

        {uploading ? (
          <div className="space-y-4">
            <div className="text-primary text-4xl">📤</div>
            <div className="text-lg font-medium text-gray-900">Uploading...</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-600">{uploadProgress}% complete</div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-gray-400 text-4xl">📁</div>
            <div className="text-lg font-medium text-gray-900">
              {dragActive ? 'Drop files here' : 'Upload Files'}
            </div>
            <div className="text-sm text-gray-600">
              Drag and drop files here, or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-primary hover:text-primary-dark font-medium"
              >
                browse
              </button>
            </div>
            <div className="text-xs text-gray-500">
              Max size: {maxSize}MB • Supported: {allowedTypes.join(', ')}
            </div>
          </div>
        )}
      </div>

      {/* File preview area */}
      <div className="mt-4 space-y-2">
        <div className="text-sm font-medium text-gray-700">Recent uploads:</div>
        <div className="text-xs text-gray-500">
          Files will appear here after upload
        </div>
      </div>
    </div>
  );
}

// File list component
interface FileListProps {
  files: any[];
  onDelete?: (fileId: number) => void;
  showActions?: boolean;
}

export function FileList({ files, onDelete, showActions = true }: FileListProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) return <PhotoIcon className="w-5 h-5" />;
    if (fileType.includes('pdf')) return <DocumentIcon className="w-5 h-5" />;
    if (fileType.includes('word')) return <DocumentIcon className="w-5 h-5" />;
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return <TableCellsIcon className="w-5 h-5" />;
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) return <PresentationChartBarIcon className="w-5 h-5" />;
    return <DocumentIcon className="w-5 h-5" />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-BE');
  };

  if (files.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2">📁</div>
        <p>No files uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {files.map((file) => (
        <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getFileIcon(file.mime_type)}</div>
              <div>
                <div className="font-medium text-gray-900">
                  {file.original_filename}
                </div>
                <div className="text-sm text-gray-500">
                  {formatFileSize(file.file_size)} • {formatDate(file.created_at)}
                </div>
                {file.description && (
                  <div className="text-sm text-gray-600 mt-1">
                    {file.description}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <a
                href={`/api/files/${file.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:text-primary-dark text-sm font-medium"
              >
                View
              </a>
              {showActions && onDelete && (
                <button
                  onClick={() => onDelete(file.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

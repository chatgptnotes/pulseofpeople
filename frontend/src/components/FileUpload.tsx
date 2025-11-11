import React, { useRef, useState } from 'react';
import { Upload, X, FileText, Image as ImageIcon, FileIcon, Plus } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (files: File | File[]) => void;
  accept?: string;
  maxSize?: number; // in bytes
  disabled?: boolean;
  multiple?: boolean; // NEW: Allow multiple file upload
  maxFiles?: number; // NEW: Maximum number of files (for multiple mode)
  showPreview?: boolean; // NEW: Show image preview
}

export default function FileUpload({
  onFileSelect,
  accept = '.csv,.jpg,.jpeg,.png,.pdf', // NEW: Support multiple file types
  maxSize = 5 * 1024 * 1024, // 5MB default
  disabled = false,
  multiple = false,
  maxFiles = 5,
  showPreview = true
}: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [error, setError] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);
  const [imagePreviews, setImagePreviews] = useState<Record<string, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Get file extension
  const getFileExtension = (filename: string): string => {
    return filename.slice(filename.lastIndexOf('.')).toLowerCase();
  };

  // Check if file is an image
  const isImage = (file: File): boolean => {
    return file.type.startsWith('image/');
  };

  // Generate image preview
  const generatePreview = (file: File) => {
    if (!isImage(file) || !showPreview) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreviews(prev => ({
        ...prev,
        [file.name]: reader.result as string
      }));
    };
    reader.readAsDataURL(file);
  };

  // Validate file type based on accept prop
  const isValidFileType = (file: File): boolean => {
    const extension = getFileExtension(file.name);
    const acceptedTypes = accept.split(',').map(t => t.trim());

    // Check if extension is in accepted list
    if (acceptedTypes.includes(extension)) {
      return true;
    }

    // Check MIME type
    if (file.type) {
      for (const acceptType of acceptedTypes) {
        if (acceptType.startsWith('.')) continue;
        if (file.type === acceptType || file.type.startsWith(acceptType.split('/')[0] + '/')) {
          return true;
        }
      }
    }

    return false;
  };

  const validateFile = (file: File): boolean => {
    // Check file type
    if (!isValidFileType(file)) {
      const acceptedExts = accept.split(',').map(t => t.trim().toUpperCase()).join(', ');
      setError(`Invalid file type. Accepted types: ${acceptedExts}`);
      return false;
    }

    // Check file size
    if (file.size > maxSize) {
      setError(`File "${file.name}" size must be less than ${(maxSize / (1024 * 1024)).toFixed(0)}MB`);
      return false;
    }

    return true;
  };

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setError('');

    const filesArray = Array.from(files);
    const validFiles: File[] = [];

    // Check max files limit
    if (multiple && selectedFiles.length + filesArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    // Validate each file
    for (const file of filesArray) {
      if (validateFile(file)) {
        validFiles.push(file);
        generatePreview(file);
      } else {
        // Error already set in validateFile
        return;
      }
    }

    if (validFiles.length > 0) {
      if (multiple) {
        const newFiles = [...selectedFiles, ...validFiles];
        setSelectedFiles(newFiles);
        onFileSelect(newFiles);
      } else {
        setSelectedFiles([validFiles[0]]);
        onFileSelect(validFiles[0]);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    handleFiles(e.dataTransfer.files);
  };

  const handleRemoveFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const removedFile = selectedFiles[index];

    // Remove preview
    if (imagePreviews[removedFile.name]) {
      const newPreviews = { ...imagePreviews };
      delete newPreviews[removedFile.name];
      setImagePreviews(newPreviews);
    }

    setSelectedFiles(newFiles);
    setError('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    // Notify parent
    if (multiple) {
      onFileSelect(newFiles);
    } else if (newFiles.length > 0) {
      onFileSelect(newFiles[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  // Get icon for file type
  const getFileIcon = (file: File) => {
    if (isImage(file)) {
      return <ImageIcon className="h-8 w-8 text-blue-600" />;
    }
    if (file.type === 'application/pdf') {
      return <FileText className="h-8 w-8 text-red-600" />;
    }
    return <FileIcon className="h-8 w-8 text-gray-600" />;
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="w-full">
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-all
          ${isDragging ? 'border-blue-500 bg-blue-50 scale-105' : 'border-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400 hover:bg-gray-50'}
          ${selectedFiles.length > 0 && !multiple ? 'p-4' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!disabled && (multiple || selectedFiles.length === 0) ? handleBrowseClick : undefined}
      >
        {selectedFiles.length === 0 ? (
          <>
            <Upload className={`h-12 w-12 mx-auto mb-4 transition-all ${isDragging ? 'text-blue-600 scale-110' : 'text-gray-400'}`} />
            <p className="text-gray-700 font-medium mb-2">
              {isDragging ? 'Drop files here' : 'Upload Files'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              {multiple ? `Drag and drop or click to browse (max ${maxFiles} files)` : 'Drag and drop or click to browse'}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept={accept}
              onChange={handleFileChange}
              className="hidden"
              disabled={disabled}
              multiple={multiple}
            />
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleBrowseClick();
              }}
              disabled={disabled}
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Choose {multiple ? 'Files' : 'File'}
            </button>
            <p className="text-xs text-gray-400 mt-3">
              Accepted: {accept.split(',').map(t => t.trim().toUpperCase()).join(', ')} •
              Max size: {(maxSize / (1024 * 1024)).toFixed(0)}MB each
            </p>
          </>
        ) : (
          <div className="space-y-3">
            {selectedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-start gap-4 bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                {/* File icon or image preview */}
                <div className="flex-shrink-0">
                  {isImage(file) && showPreview && imagePreviews[file.name] ? (
                    <img
                      src={imagePreviews[file.name]}
                      alt={file.name}
                      className="h-16 w-16 object-cover rounded border border-gray-300"
                    />
                  ) : (
                    getFileIcon(file)
                  )}
                </div>

                {/* File info */}
                <div className="flex-1 text-left min-w-0">
                  <p className="text-gray-900 font-medium truncate" title={file.name}>
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                  </p>
                  {isImage(file) && (
                    <p className="text-xs text-blue-600 mt-1">Image file</p>
                  )}
                  {file.type === 'application/pdf' && (
                    <p className="text-xs text-red-600 mt-1">PDF document</p>
                  )}
                </div>

                {/* Remove button */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile(index);
                  }}
                  disabled={disabled}
                  className="text-red-600 hover:text-red-800 p-2 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                  title="Remove file"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}

            {/* Add more files button (for multiple mode) */}
            {multiple && selectedFiles.length < maxFiles && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleBrowseClick();
                }}
                disabled={disabled}
                className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add More Files ({selectedFiles.length}/{maxFiles})
              </button>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600 flex items-start gap-2">
          <X className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* File count indicator (for multiple mode) */}
      {multiple && selectedFiles.length > 0 && (
        <div className="mt-2 text-sm text-gray-600">
          {selectedFiles.length} {selectedFiles.length === 1 ? 'file' : 'files'} selected
        </div>
      )}
    </div>
  );
}

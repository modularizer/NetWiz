/**
 * File Upload Component
 *
 * A drag-and-drop file upload component for netlist JSON files:
 * - Drag and drop support
 * - File type validation
 * - Upload progress indication
 * - Error handling
 */

import React, { useCallback, useState } from 'react'
import { Upload, X, Loader2 } from 'lucide-react'

interface FileUploadProps {
  onUpload: (file: File) => void
  disabled?: boolean
  acceptedTypes?: string[]
  maxSize?: number // in MB
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  disabled = false,
  acceptedTypes = ['.json'],
  maxSize = 10, // 10MB default
}) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateFile = useCallback((file: File): string | null => {
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!acceptedTypes.includes(fileExtension)) {
      return `File type ${fileExtension} is not supported. Please upload a JSON file.`
    }

    // Check file size
    if (file.size > maxSize * 1024 * 1024) {
      return `File size exceeds ${maxSize}MB limit.`
    }

    return null
  }, [acceptedTypes, maxSize])

  const handleFileSelect = useCallback((file: File) => {
    setError(null)

    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    onUpload(file)
  }, [onUpload, validateFile])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    if (disabled) return

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [disabled, handleFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragOver(true)
    }
  }, [disabled])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  return (
    <div className="relative">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-3 transition-colors
          ${isDragOver && !disabled ? 'border-primary-400 bg-primary-50' : 'border-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 flex items-center justify-center">
            {disabled ? (
              <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
            ) : (
              <Upload className="w-4 h-4 text-gray-400" />
            )}
          </div>

          <div className="text-left">
            <p className="text-sm font-medium text-gray-900">
              {disabled ? 'Uploading...' : 'Upload JSON file'}
            </p>
            <p className="text-xs text-gray-500">
              Drag & drop or click to browse
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-2 p-3 bg-error-50 border border-error-200 rounded-md">
          <div className="flex items-start space-x-2">
            <X className="w-4 h-4 text-error-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-error-700">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload

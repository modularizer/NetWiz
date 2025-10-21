/**
 * Custom React Hooks for NetWiz API Operations
 *
 * These hooks provide a clean interface for API operations with:
 * - Automatic loading states
 * - Error handling
 * - React Query integration for caching and background updates
 */

import { useMutation } from 'react-query'
import { apiClient } from '@/services/api'


// Hook for netlist upload
export const useNetlistUpload = () => {
  const mutation = useMutation({
    mutationFn: async ({ file, filename }: { file: File; filename?: string }) => {
      return await apiClient.uploadFile(file, filename)
    },
    onError: (error) => {
      console.error('Upload failed:', error)
    },
  })

  return {
    uploadNetlist: mutation.mutateAsync,
    isUploading: mutation.isLoading,
    uploadError: mutation.error,
    uploadResult: mutation.data,
  }
}

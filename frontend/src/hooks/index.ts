/**
 * Custom React Hooks for NetWiz API Operations
 *
 * These hooks provide a clean interface for API operations with:
 * - Automatic loading states
 * - Error handling
 * - React Query integration for caching and background updates
 */

import { useMutation, useQuery } from 'react-query'
import { apiClient } from '@/services/api'
import type { Netlist, ValidationResult } from '@/types/netlist'

// Hook for netlist validation
export const useNetlistValidation = () => {
  const mutation = useMutation<ValidationResult, Error, Netlist>({
    mutationFn: async (netlist: Netlist) => {
        try {
            const response = await apiClient.validateNetlist(netlist)
            return response.validation_result
        }catch(e){
            console.log("handling validation error", e)
            const vr = e.details?.validation_result;
            if (!vr){
                throw new Error("No validation result found")
            }
            return vr
        }

    },
    onError: (error) => {
      console.error('Validation failed-onerror:', error)
    },
  })

  return {
    validateNetlist: mutation.mutateAsync,
    isValidating: mutation.isLoading,
    validationError: mutation.error,
    validationResult: mutation.data,
  }
}

// Hook for netlist upload
export const useNetlistUpload = () => {
  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.uploadFile(file)
      return response
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

// Hook for fetching a specific netlist
export const useNetlist = (submissionId: string) => {
  return useQuery({
    queryKey: ['netlist', submissionId],
    queryFn: async () => {
      const response = await apiClient.getNetlist(submissionId)
      return response.submission
    },
    enabled: !!submissionId,
  })
}

// Hook for listing netlists
export const useNetlists = (params?: { page?: number; page_size?: number; user_id?: string }) => {
  return useQuery({
    queryKey: ['netlists', params],
    queryFn: async () => {
      const response = await apiClient.listNetlists(params)
      return response
    },
  })
}

// Hook for health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await apiClient.getHealth()
      return response
    },
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  })
}

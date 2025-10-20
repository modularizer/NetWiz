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

// Hook for JSON text validation
export const useJsonValidation = () => {
  const mutation = useMutation<ValidationResult, Error, string>({
    mutationFn: async (jsonText: string) => {
      console.log('🎯 JSON Hook mutationFn: Starting validation')
      console.log('🎯 JSON Hook mutationFn: JSON text length:', jsonText.length)
      try {
        console.log('🎯 JSON Hook mutationFn: About to call API client')
        const response = await apiClient.validateJsonText(jsonText)
        console.log('🎯 JSON Hook mutationFn: API client returned success:', response)
        return response.validation_result
      } catch (error: any) {
        console.log('🎯 JSON Hook mutationFn: Caught error:', error)
        console.log('🎯 JSON Hook mutationFn: Error.details:', error.details)
        console.log('🎯 JSON Hook mutationFn: Error.details.validation_result:', error.details?.validation_result)

        // Always return a validation result, never throw
        if (error.details?.validation_result) {
          console.log('🎯 JSON Hook mutationFn: Returning validation result from error.details')
          return error.details.validation_result
        }

        console.log('🎯 JSON Hook mutationFn: Creating generic error result')
        return {
          is_valid: false,
          errors: [{
            message: error.message || 'JSON validation failed',
            error_type: {
              name: 'validation_error',
              description: 'An unhandled validation error occurred'
            },
            severity: 'error',
            location: null
          }],
          warnings: [],
          validation_timestamp: new Date().toISOString(),
          validation_rules_applied: []
        }
      }
    },
    onError: (error) => {
      console.error('🎯 JSON Hook onError:', error)
    },
    onSuccess: (data) => {
      console.log('🎯 JSON Hook onSuccess:', data)
      console.log('🎯 JSON Hook onSuccess: is_valid:', data?.is_valid)
      console.log('🎯 JSON Hook onSuccess: errors count:', data?.errors?.length || 0)
    },
  })

  console.log('🎯 JSON Hook: Current mutation.data:', mutation.data)
  console.log('🎯 JSON Hook: Current mutation.error:', mutation.error)
  console.log('🎯 JSON Hook: Current mutation.isLoading:', mutation.isLoading)

  return {
    validateJsonText: mutation.mutateAsync,
    isValidating: mutation.isLoading,
    validationError: mutation.error,
    validationResult: mutation.data,
  }
}

// Hook for netlist validation
export const useNetlistValidation = () => {
  const mutation = useMutation<ValidationResult, Error, Netlist>({
    mutationFn: async (netlist: Netlist) => {
      console.log('🎯 Hook mutationFn: Starting validation')
      console.log('🎯 Hook mutationFn: Netlist:', netlist)
      try {
        console.log('🎯 Hook mutationFn: About to call API client')
        const response = await apiClient.validateNetlist(netlist)
        console.log('🎯 Hook mutationFn: API client returned success:', response)
        return response.validation_result
      } catch (error: any) {
        console.log('🎯 Hook mutationFn: Caught error:', error)
        console.log('🎯 Hook mutationFn: Error.details:', error.details)
        console.log('🎯 Hook mutationFn: Error.details.validation_result:', error.details?.validation_result)

        // Always return a validation result, never throw
        if (error.details?.validation_result) {
          console.log('🎯 Hook mutationFn: Returning validation result from error.details')
          return error.details.validation_result
        }

        console.log('🎯 Hook mutationFn: Creating generic error result')
        return {
          is_valid: false,
          errors: [{
            message: error.message || 'Validation failed',
            error_type: {
              name: 'validation_error',
              description: 'An unhandled validation error occurred'
            },
            severity: 'error',
            location: null
          }],
          warnings: [],
          validation_rules_applied: []
        }
      }
    },
    onError: (error) => {
      console.error('🎯 Hook onError:', error)
    },
    onSuccess: (data) => {
      console.log('🎯 Hook onSuccess:', data)
      console.log('🎯 Hook onSuccess: is_valid:', data?.is_valid)
      console.log('🎯 Hook onSuccess: errors count:', data?.errors?.length || 0)
    },
  })

  console.log('🎯 Hook: Current mutation.data:', mutation.data)
  console.log('🎯 Hook: Current mutation.error:', mutation.error)
  console.log('🎯 Hook: Current mutation.isLoading:', mutation.isLoading)

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
    mutationFn: async ({ file, filename }: { file: File; filename?: string }) => {
      const response = await apiClient.uploadFile(file, filename)
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
      const submission = await apiClient.getNetlist(submissionId)
      return submission
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

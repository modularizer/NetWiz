/**
 * API Client for NetWiz Backend
 *
 * This module provides a type-safe API client for communicating with the
 * NetWiz backend. It uses the generated TypeScript types from the OpenAPI
 * schema to ensure type safety across the frontend-backend boundary.
 *
 * Features:
 * - Type-safe API calls using generated OpenAPI types
 * - Automatic error handling and response parsing
 * - Request/response interceptors for logging and error handling
 * - Support for file uploads and JSON payloads
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type { paths, components } from '@/types/api'
import type {
  NetlistUploadRequest,
  NetlistUploadResponse,
  ValidationResponse
} from '@/types/netlist'

// Type aliases for better readability
type ApiPaths = paths
type ApiComponents = components

// Request/Response type helpers (for future use)
// type ApiRequest<T extends keyof ApiPaths> = ApiPaths[T] extends {
//   post: { requestBody: { content: { 'application/json': infer R } } }
// }
//   ? R
//   : never

// type ApiResponse<T extends keyof ApiPaths, M extends keyof ApiPaths[T]> =
//   ApiPaths[T][M] extends { responses: { 200: { content: { 'application/json': infer R } } } }
//     ? R
//     : never

// API Error type
export interface ApiError {
  message: string
  status?: number
  details?: any
}

// Configuration
let API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL || 'http://localhost:5000'
const API_TIMEOUT = 30000 // 30 seconds

// Function to update API base URL
export const updateApiBaseUrl = (newBaseUrl: string) => {
  API_BASE_URL = newBaseUrl
  // Recreate the client with new base URL
  apiClient.updateBaseUrl(newBaseUrl)
}

class NetWizApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  updateBaseUrl(newBaseUrl: string) {
    this.client.defaults.baseURL = newBaseUrl
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('❌ API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error: AxiosError) => {
        console.error('❌ API Response Error:', error.response?.status, error.message)
        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      return {
        message: (error.response.data as any)?.detail || error.message,
        status: error.response.status,
        details: error.response.data,
      }
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Network error - no response from server',
        status: 0,
      }
    } else {
      // Something else happened
      return {
        message: error.message,
      }
    }
  }

  // Health check
  async getHealth(): Promise<ApiComponents['schemas']['HealthResponse']> {
    const response = await this.client.get<ApiComponents['schemas']['HealthResponse']>('/health')
    return response.data
  }

  // Netlist operations
  async uploadNetlist(
    data: NetlistUploadRequest
  ): Promise<NetlistUploadResponse> {
    const response = await this.client.post<NetlistUploadResponse>(
      '/netlist/upload',
      data
    )
    return response.data
  }

  async validateNetlist(
    netlist: any
  ): Promise<ValidationResponse> {
    const response = await this.client.post<ValidationResponse>(
      '/netlist/validate',
      netlist, // Wrap in ValidationRequest format
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  }

  async validateJsonText(
    jsonText: string
  ): Promise<ValidationResponse> {
    const response = await this.client.post<ValidationResponse>(
      '/netlist/validate-text',
      { json_text: jsonText },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  }

  async getNetlist(submissionId: string): Promise<ApiComponents['schemas']['NetlistGetResponse']> {
    const response = await this.client.get<ApiComponents['schemas']['NetlistGetResponse']>(
      `/netlist/${submissionId}`
    )
    return response.data
  }

  async listNetlists(params?: {
    page?: number
    page_size?: number
    user_id?: string
  }): Promise<ApiComponents['schemas']['NetlistListResponse']> {
    const response = await this.client.get<ApiComponents['schemas']['NetlistListResponse']>(
      '/netlist',
      { params }
    )
    return response.data
  }

  // File upload helper
  async uploadFile(file: File, userId?: string): Promise<NetlistUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (userId) {
      formData.append('user_id', userId)
    }

    const response = await this.client.post<NetlistUploadResponse>(
      '/netlist/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }
}

// Create and export singleton instance
export const apiClient = new NetWizApiClient()

// Export types for use in components
export type {
  ApiComponents,
  ApiPaths,
}

// Export commonly used types
export type {
  Netlist,
  ValidationResult,
  ValidationError,
  Component,
  Net,
  Pin,
  NetConnection,
  NetlistUploadRequest,
  NetlistUploadResponse,
  ValidationRequest,
  ValidationResponse
} from '@/types/netlist'

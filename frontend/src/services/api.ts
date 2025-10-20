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

import axios, { AxiosInstance } from 'axios'
import type { paths, components } from '@/types/api'
import type {
  NetlistSubmission,
  ValidationResponse
} from '@/types/netlist'
import type {
  User,
  Token,
  UserLogin,
  UserCreate,
  ChangePasswordRequest,
  RefreshTokenRequest
} from '@/types/auth'

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
const DEFAULT_API_URL = 'http://localhost:5000'
const API_URL_STORAGE_KEY = 'netwiz-api-url'

const getApiBaseUrl = () => {
  // Check localStorage for cached API URL first
  const cachedUrl = localStorage.getItem(API_URL_STORAGE_KEY)
  if (cachedUrl) {
    return cachedUrl
  }

  // Fallback to default localhost URL
  return DEFAULT_API_URL
}

let API_BASE_URL = getApiBaseUrl()
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
  }

  updateBaseUrl(newBaseUrl: string) {
    this.client.defaults.baseURL = newBaseUrl
  }


  private getAuthHeaders() {
    const token = localStorage.getItem('netwiz_access_token')
    console.log('🔑 getAuthHeaders - Token:', token ? 'Found' : 'Not found')
    console.log('🔑 getAuthHeaders - Token value:', token ? `${token.substring(0, 20)}...` : 'null')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    console.log('🔑 getAuthHeaders - Headers:', headers)
    return headers
  }



  // Health check
  async getHealth(): Promise<ApiComponents['schemas']['HealthResponse']> {
    const response = await this.client.get<ApiComponents['schemas']['HealthResponse']>('/health')
    return response.data
  }

  // Authentication methods
  async signin(credentials: UserLogin): Promise<Token> {
    const response = await this.client.post<Token>('/auth/signin', credentials)
    return response.data
  }

  async signup(userData: UserCreate): Promise<User> {
    const response = await this.client.post<User>('/auth/signup', userData)
    return response.data
  }

  async signout(): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>('/auth/signout', {}, {
      headers: this.getAuthHeaders()
    })
    return response.data
  }

  async refreshToken(refreshData: RefreshTokenRequest): Promise<Token> {
    const response = await this.client.post<Token>('/auth/refresh', refreshData)
    return response.data
  }

  async changePassword(passwordData: ChangePasswordRequest): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>('/auth/change-password', passwordData, {
      headers: this.getAuthHeaders()
    })
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const authHeaders = this.getAuthHeaders()
    console.log('🔑 getCurrentUser - Making request with headers:', authHeaders)
    console.log('🔑 getCurrentUser - Client default headers:', this.client.defaults.headers)

    const response = await this.client.get<User>('/auth/me', {
      headers: {
        ...this.client.defaults.headers.common,
        ...authHeaders
      }
    })
    console.log('🔑 getCurrentUser - Final request headers:', response.config.headers)
    return response.data
  }

  async getUserById(userId: string): Promise<User> {
    const response = await this.client.get<User>(
      `/auth/user/${userId}`,
      {
        headers: {
          ...this.getAuthHeaders(),
        }
      }
    )
    return response.data
  }

  async checkUsernameAvailability(username: string): Promise<{
    username: string
    available: boolean
    message: string
  }> {
    const response = await this.client.post<{
      username: string
      available: boolean
      message: string
    }>('/auth/check-username', { username })
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
          ...this.getAuthHeaders(),
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
          ...this.getAuthHeaders(),
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  }

  async getNetlist(submissionId: string): Promise<NetlistSubmission> {
    const response = await this.client.get<NetlistSubmission>(
      `/netlist/${submissionId}`,
      {
        headers: {
          ...this.getAuthHeaders(),
        }
      }
    )
    return response.data
  }

  async listNetlists(params?: {
    page?: number
    page_size?: number
    user_id?: string
    list_all?: boolean
  }): Promise<ApiComponents['schemas']['NetlistListResponse']> {
    const response = await this.client.get<ApiComponents['schemas']['NetlistListResponse']>(
      '/netlist',
      {
        params,
        headers: {
          ...this.getAuthHeaders(),
        }
      }
    )
    return response.data
  }

  async uploadFile(file: File, filename?: string): Promise<NetlistSubmission> {
    const formData = new FormData()
    formData.append('file', file)
    if (filename) {
      formData.append('filename', filename)
    }

    const response = await this.client.post<NetlistSubmission>(
      '/netlist/upload',
      formData,
      {
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }
}

// Create and export singleton instance
export const apiClient = new NetWizApiClient()

// Export the default API URL and storage key for use in other components
export { DEFAULT_API_URL, API_URL_STORAGE_KEY }

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
  NetlistSubmission,
  ValidationRequest,
  ValidationResponse
} from '@/types/netlist'

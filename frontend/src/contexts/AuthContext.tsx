/**
 * Authentication Context for NetWiz Frontend
 *
 * Provides authentication state management and methods for signin/signout/change password
 * with automatic token refresh functionality.
 */

import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { AuthState, AuthContextType, User, Token, UserLogin, UserCreate, ChangePasswordRequest } from '@/types/auth'
import { apiClient } from '@/services/api'
import { clearAllAuthData, getStoredAuthData } from '@/utils/authUtils'

// Storage keys
const ACCESS_TOKEN_KEY = 'netwiz_access_token'
const REFRESH_TOKEN_KEY = 'netwiz_refresh_token'
const USER_KEY = 'netwiz_user'

// Auth action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: Token } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'TOKEN_REFRESH'; payload: Token }

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

// Auth reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      }
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }
    case 'TOKEN_REFRESH':
      return {
        ...state,
        token: action.payload,
        error: null,
      }
    default:
      return state
  }
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Auth provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Load stored auth data on mount
  useEffect(() => {
    const loadStoredAuth = async () => {
      try {
        const storedData = getStoredAuthData()

        if (storedData && storedData.refreshToken) {
          const { accessToken, refreshToken } = storedData

          const token: Token = {
            access_token: accessToken,
            refresh_token: refreshToken,
            token_type: 'bearer',
            expires_in: 0, // Will be refreshed
            refresh_expires_in: 0, // Will be refreshed
          }

          // Verify token is still valid by getting current user
          try {
            const currentUser = await apiClient.getCurrentUser()
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: { user: currentUser, token },
            })
          } catch (error) {
            // Token is invalid, try to refresh
            try {
              const refreshResponse = await apiClient.refreshToken({ refresh_token: refreshToken })

              // Store the new tokens first
              storeAuthData(storedData.user, refreshResponse)

              // Get updated user data with new token
              const currentUser = await apiClient.getCurrentUser()

              // Update stored user data
              storeAuthData(currentUser, refreshResponse)

              dispatch({
                type: 'AUTH_SUCCESS',
                payload: { user: currentUser, token: refreshResponse },
              })
            } catch (refreshError) {
              // Refresh failed, clear stored data
              console.error('Token refresh failed during initial load:', refreshError)
              clearAllAuthData()
              dispatch({ type: 'AUTH_LOGOUT' })
            }
          }
        } else {
          // No stored data, user needs to sign in
          dispatch({ type: 'AUTH_LOGOUT' })
        }
      } catch (error) {
        console.error('Error loading stored auth:', error)
        clearAllAuthData()
        dispatch({ type: 'AUTH_LOGOUT' })
      }
    }

    loadStoredAuth()
  }, [])

  // Store auth data in localStorage
  const storeAuthData = (user: User, token: Token) => {
    console.log('💾 Storing auth data:', {
      username: user.username,
      tokenLength: token.access_token.length,
      tokenStart: token.access_token.substring(0, 20) + '...'
    })
    localStorage.setItem(ACCESS_TOKEN_KEY, token.access_token)
    localStorage.setItem(REFRESH_TOKEN_KEY, token.refresh_token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    console.log('💾 Token stored, verifying:', localStorage.getItem(ACCESS_TOKEN_KEY) ? 'Success' : 'Failed')
  }

  // Clear stored auth data
  const clearStoredAuth = () => {
    clearAllAuthData()
  }

  // Sign in
  const signin = async (credentials: UserLogin) => {
    dispatch({ type: 'AUTH_START' })
    try {
      const token = await apiClient.signin(credentials)

      // Store the token FIRST before making authenticated requests
      storeAuthData({ username: credentials.username } as User, token)

      // Now get the full user data with the stored token
      const user = await apiClient.getCurrentUser()

      // Update the stored user data with the full user object
      storeAuthData(user, token)
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token },
      })
    } catch (error: any) {
      // Extract error message from API response
      let errorMessage = 'Sign in failed'

      if (error.details?.error) {
        errorMessage = error.details.error
      } else if (error.details?.message) {
        errorMessage = error.details.message
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }

      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw error
    }
  }

  // Sign up
  const signup = async (userData: UserCreate) => {
    dispatch({ type: 'AUTH_START' })
    try {
      await apiClient.signup(userData)
      // After successful signup, automatically sign in
      await signin({ username: userData.username, password: userData.password })
    } catch (error: any) {
      const errorMessage = error.message || 'Sign up failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw error
    }
  }

  // Sign out
  const signout = async () => {
    try {
      if (state.isAuthenticated) {
        await apiClient.signout()
      }
    } catch (error) {
      console.error('Error during signout:', error)
    } finally {
      clearStoredAuth()
      dispatch({ type: 'AUTH_LOGOUT' })
    }
  }

  // Change password
  const changePassword = async (passwordData: ChangePasswordRequest) => {
    try {
      await apiClient.changePassword(passwordData)
    } catch (error: any) {
      const errorMessage = error.message || 'Password change failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw error
    }
  }

  // Refresh token
  const refreshToken = async (): Promise<void> => {
    try {
      const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      if (!storedRefreshToken) {
        // No refresh token available - this is normal when user hasn't signed in
        clearStoredAuth()
        dispatch({ type: 'AUTH_LOGOUT' })
        return
      }

      const token = await apiClient.refreshToken({ refresh_token: storedRefreshToken })

      // Get current user data to update stored user info
      const currentUser = await apiClient.getCurrentUser()

      // Store the new tokens and user data
      storeAuthData(currentUser, token)

      dispatch({ type: 'TOKEN_REFRESH', payload: token })
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearStoredAuth()
      dispatch({ type: 'AUTH_LOGOUT' })
      throw error
    }
  }

  // Clear error
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const contextValue: AuthContextType = {
    ...state,
    signin,
    signup,
    signout,
    changePassword,
    refreshToken,
    clearError,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

/**
 * Token Refresh Hook
 *
 * Provides automatic background token refresh functionality.
 * Monitors token expiration and refreshes tokens before they expire.
 */

import { useEffect, useRef } from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface TokenRefreshOptions {
  refreshThresholdMinutes?: number // Refresh token when this many minutes remain
  checkIntervalMinutes?: number    // How often to check token expiration
}

export function useTokenRefresh(options: TokenRefreshOptions = {}) {
  const { token, refreshToken, isAuthenticated } = useAuth()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const {
    refreshThresholdMinutes = 5, // Default: refresh 5 minutes before expiry
    checkIntervalMinutes = 1      // Default: check every minute
  } = options

  useEffect(() => {
    if (!isAuthenticated || !token) {
      // Clear any existing interval if not authenticated
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    const checkTokenExpiration = () => {
      try {
        // Parse JWT token to get expiration time
        const tokenPayload = JSON.parse(atob(token.access_token.split('.')[1]))
        const expirationTime = tokenPayload.exp * 1000 // Convert to milliseconds
        const currentTime = Date.now()
        const timeUntilExpiry = expirationTime - currentTime
        const refreshThreshold = refreshThresholdMinutes * 60 * 1000 // Convert to milliseconds

        // If token expires within the threshold, refresh it
        if (timeUntilExpiry <= refreshThreshold) {
          console.log('Token expires soon, refreshing...')
          refreshToken().catch((error) => {
            console.error('Background token refresh failed:', error)
          })
        }
      } catch (error) {
        console.error('Error checking token expiration:', error)
        // If we can't parse the token, try to refresh it
        refreshToken().catch((refreshError) => {
          console.error('Background token refresh failed:', refreshError)
        })
      }
    }

    // Check immediately
    checkTokenExpiration()

    // Set up interval to check periodically
    intervalRef.current = setInterval(
      checkTokenExpiration,
      checkIntervalMinutes * 60 * 1000 // Convert to milliseconds
    )

    // Cleanup function
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isAuthenticated, token, refreshToken, refreshThresholdMinutes, checkIntervalMinutes])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])
}

/**
 * Authentication Utilities
 *
 * Helper functions for managing authentication state and clearing data
 */

// Storage keys
const ACCESS_TOKEN_KEY = 'netwiz_access_token'
const REFRESH_TOKEN_KEY = 'netwiz_refresh_token'
const USER_KEY = 'netwiz_user'
const USERNAME_CACHE_KEY = 'netwiz_cached_username'

/**
 * Clear all authentication data from localStorage
 */
export function clearAllAuthData() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(USERNAME_CACHE_KEY)
  console.log('All authentication data cleared')
}

/**
 * Check if user has any stored authentication data
 */
export function hasStoredAuthData(): boolean {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  const user = localStorage.getItem(USER_KEY)

  return !!(accessToken && refreshToken && user)
}

/**
 * Get stored authentication data
 */
export function getStoredAuthData() {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  const userStr = localStorage.getItem(USER_KEY)

  if (!accessToken || !refreshToken || !userStr) {
    return null
  }

  try {
    const user = JSON.parse(userStr)
    return {
      accessToken,
      refreshToken,
      user
    }
  } catch (error) {
    console.error('Error parsing stored user data:', error)
    clearAllAuthData()
    return null
  }
}

/**
 * Get cached username
 */
export function getCachedUsername(): string | null {
  return localStorage.getItem(USERNAME_CACHE_KEY)
}

/**
 * Set cached username
 */
export function setCachedUsername(username: string) {
  localStorage.setItem(USERNAME_CACHE_KEY, username)
}

/**
 * Clear cached username
 */
export function clearCachedUsername() {
  localStorage.removeItem(USERNAME_CACHE_KEY)
}

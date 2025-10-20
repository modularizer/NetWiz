/**
 * Username validation utilities
 *
 * Enforces the same validation rules as the backend:
 * - 3-20 characters long
 * - Only lowercase letters, numbers, and dashes
 * - Must start with a letter
 * - Cannot end with dash
 * - Cannot have consecutive dashes
 */

export interface UsernameValidationResult {
  isValid: boolean
  message: string
}

export function validateUsername(username: string): UsernameValidationResult {
  // Check length
  if (username.length < 3) {
    return {
      isValid: false,
      message: `Username '${username}' must be at least 3 characters long`
    }
  }

  if (username.length > 20) {
    return {
      isValid: false,
      message: `Username '${username}' must be no more than 20 characters long`
    }
  }

  // Must be lowercase
  if (username !== username.toLowerCase()) {
    return {
      isValid: false,
      message: `Username '${username}' must be lowercase`
    }
  }

  // Check for invalid characters (only lowercase letters, numbers and dashes allowed)
  if (!/^[a-z0-9-]+$/.test(username)) {
    return {
      isValid: false,
      message: `Username '${username}' can only contain lowercase letters, numbers, and dashes`
    }
  }

  // Must start with a letter
  if (!/^[a-z]/.test(username)) {
    return {
      isValid: false,
      message: `Username '${username}' must start with a letter`
    }
  }

  // Cannot end with dash
  if (username.endsWith('-')) {
    return {
      isValid: false,
      message: `Username '${username}' cannot end with a dash`
    }
  }

  // Cannot have consecutive dashes
  if (username.includes('--')) {
    return {
      isValid: false,
      message: `Username '${username}' cannot have consecutive dashes`
    }
  }

  return {
    isValid: true,
    message: `Username '${username}' format is valid`
  }
}

export function sanitizeUsername(username: string): string {
  // Convert to lowercase and remove invalid characters, keeping only lowercase letters, numbers and dashes
  return username.toLowerCase().replace(/[^a-z0-9-]/g, '')
}

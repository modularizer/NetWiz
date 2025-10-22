/**
 * Sign Up Component
 *
 * Provides a form for user registration with username and password.
 * Includes validation and error handling.
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Eye, EyeOff, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { UserCreate } from '@/types/auth'
import { apiClient } from '@/services/api'
import { validateUsername, sanitizeUsername } from '@/utils/usernameValidation'

interface SignUpFormProps {
  onSuccess?: () => void
  onSwitchToSignIn?: () => void
}

export function SignUpForm({ onSuccess, onSwitchToSignIn }: SignUpFormProps) {
  const { signup, isLoading, error, clearError } = useAuth()
  const [formData, setFormData] = useState<UserCreate & { confirmPassword: string }>({
    username: '',
    password: '',
    confirmPassword: '',
  })
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  // Username availability checking state
  const [usernameStatus, setUsernameStatus] = useState<{
    checking: boolean
    available: boolean | null
    message: string
  }>({
    checking: false,
    available: null,
    message: ''
  })

  const validateForm = () => {
    const errors: Record<string, string> = {}

    // Validate username format first
    const usernameValidation = validateUsername(formData.username)
    if (!usernameValidation.isValid) {
      errors.username = usernameValidation.message
    } else if (usernameStatus.available === false) {
      errors.username = usernameStatus.message
    }

    if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters long'
    }

    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Debounced username availability check
  const checkUsernameAvailability = useCallback(async (username: string) => {
    if (!username || username.length < 3) {
      setUsernameStatus({
        checking: false,
        available: null,
        message: ''
      })
      return
    }

    // First check format validation
    const formatValidation = validateUsername(username)
    if (!formatValidation.isValid) {
      setUsernameStatus({
        checking: false,
        available: false,
        message: formatValidation.message
      })
      return
    }

    setUsernameStatus(prev => ({ ...prev, checking: true }))

    try {
      const result = await apiClient.checkUsernameAvailability(username)
      setUsernameStatus({
        checking: false,
        available: result.available,
        message: result.message
      })
    } catch (error) {
      setUsernameStatus({
        checking: false,
        available: false,
        message: 'Error checking username availability'
      })
    }
  }, [])

  // Debounce username checking
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      checkUsernameAvailability(formData.username)
    }, 500) // 500ms delay

    return () => clearTimeout(timeoutId)
  }, [formData.username, checkUsernameAvailability])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setValidationErrors({})

    if (!validateForm()) {
      return
    }

    try {
      await signup({
        username: formData.username,
        password: formData.password,
      })
      onSuccess?.()
    } catch (error) {
      // Error is handled by the auth context
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    let processedValue = value

    // Auto-convert username to lowercase
    if (name === 'username') {
      processedValue = sanitizeUsername(value)
    }

    setFormData(prev => ({ ...prev, [name]: processedValue }))

    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="max-w-lg mx-auto bg-white rounded-lg shadow-md p-6 flex-1 flex flex-col">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign Up</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 flex-1 flex flex-col">
        <div className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <div className="relative">
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                className={`w-full px-3 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  validationErrors.username ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your username (lowercase letters, numbers, dashes)"
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                {usernameStatus.checking ? (
                  <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />
                ) : usernameStatus.available === true ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : usernameStatus.available === false ? (
                  <XCircle className="h-4 w-4 text-red-500" />
                ) : null}
              </div>
            </div>
            {validationErrors.username && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
            )}
            {!validationErrors.username && usernameStatus.message && (
              <p className={`mt-1 text-sm ${
                usernameStatus.available === true ? 'text-green-600' :
                usernameStatus.available === false ? 'text-red-600' :
                'text-gray-500'
              }`}>
                {usernameStatus.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className={`w-full px-3 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  validationErrors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {validationErrors.password && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className={`w-full px-3 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  validationErrors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Confirm your password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {validationErrors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
            )}
          </div>
        </div>

        <div className="mt-auto space-y-4">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </button>

          {onSwitchToSignIn && (
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={onSwitchToSignIn}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Sign in
                </button>
              </p>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}

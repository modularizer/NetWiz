/**
 * Change Password Component
 *
 * Provides a form for authenticated users to change their password.
 * Requires current password verification.
 */

import React, { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { ChangePasswordRequest } from '@/types/auth'

interface ChangePasswordFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export function ChangePasswordForm({ onSuccess, onCancel }: ChangePasswordFormProps) {
  const { changePassword, isLoading, error, clearError } = useAuth()
  const [formData, setFormData] = useState<ChangePasswordRequest & { confirmNewPassword: string }>({
    current_password: '',
    new_password: '',
    confirmNewPassword: '',
  })
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const errors: Record<string, string> = {}

    if (formData.current_password.length === 0) {
      errors.current_password = 'Current password is required'
    }

    if (formData.new_password.length < 6) {
      errors.new_password = 'New password must be at least 6 characters long'
    }

    if (formData.new_password === formData.current_password) {
      errors.new_password = 'New password must be different from current password'
    }

    if (formData.new_password !== formData.confirmNewPassword) {
      errors.confirmNewPassword = 'New passwords do not match'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setValidationErrors({})

    if (!validateForm()) {
      return
    }

    try {
      await changePassword({
        current_password: formData.current_password,
        new_password: formData.new_password,
      })

      // Clear form on success
      setFormData({
        current_password: '',
        new_password: '',
        confirmNewPassword: '',
      })

      onSuccess?.()
    } catch (error) {
      // Error is handled by the auth context
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Change Password</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
            Current Password
          </label>
          <input
            type="password"
            id="current_password"
            name="current_password"
            value={formData.current_password}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              validationErrors.current_password ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter your current password"
          />
          {validationErrors.current_password && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.current_password}</p>
          )}
        </div>

        <div>
          <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
            New Password
          </label>
          <input
            type="password"
            id="new_password"
            name="new_password"
            value={formData.new_password}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              validationErrors.new_password ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter your new password"
          />
          {validationErrors.new_password && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.new_password}</p>
          )}
        </div>

        <div>
          <label htmlFor="confirmNewPassword" className="block text-sm font-medium text-gray-700 mb-1">
            Confirm New Password
          </label>
          <input
            type="password"
            id="confirmNewPassword"
            name="confirmNewPassword"
            value={formData.confirmNewPassword}
            onChange={handleChange}
            required
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              validationErrors.confirmNewPassword ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Confirm your new password"
          />
          {validationErrors.confirmNewPassword && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.confirmNewPassword}</p>
          )}
        </div>

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Changing Password...' : 'Change Password'}
          </button>

          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

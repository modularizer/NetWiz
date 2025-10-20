/**
 * User Profile Component
 *
 * Displays user information and provides access to account management features
 * like changing password and signing out.
 */

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { ChangePasswordForm } from './ChangePasswordForm'

export function UserProfile() {
  const { user, signout, isLoading } = useAuth()
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [showSignOutConfirm, setShowSignOutConfirm] = useState(false)

  const handleSignOut = async () => {
    try {
      await signout()
      setShowSignOutConfirm(false)
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  if (!user) {
    return null
  }

  if (showChangePassword) {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <ChangePasswordForm
          onSuccess={() => setShowChangePassword(false)}
          onCancel={() => setShowChangePassword(false)}
        />
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">User Profile</h2>

      <div className="space-y-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Account Information</h3>

          <div className="space-y-2">
            <div>
              <span className="text-sm font-medium text-gray-600">Username:</span>
              <span className="ml-2 text-gray-900">{user.username}</span>
            </div>

            <div>
              <span className="text-sm font-medium text-gray-600">User Type:</span>
              <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                user.user_type === 'admin'
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {user.user_type}
              </span>
            </div>

            <div>
              <span className="text-sm font-medium text-gray-600">Account Status:</span>
              <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                user.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div>
              <span className="text-sm font-medium text-gray-600">Member Since:</span>
              <span className="ml-2 text-gray-900">
                {new Date(user.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => setShowChangePassword(true)}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Change Password
          </button>

          <button
            onClick={() => setShowSignOutConfirm(true)}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* Sign Out Confirmation Modal */}
      {showSignOutConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Confirm Sign Out</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to sign out? You'll need to sign in again to access your account.
            </p>

            <div className="flex space-x-3">
              <button
                onClick={handleSignOut}
                disabled={isLoading}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing Out...' : 'Sign Out'}
              </button>

              <button
                onClick={() => setShowSignOutConfirm(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Authentication Demo Page
 *
 * Demonstrates the authentication system with sign in/up forms
 * and user profile management.
 */

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { AuthModal, UserProfile, ProtectedRoute } from '@/components/auth'
import { NetWizHeader } from '@/components/layout/NetWizHeader'

export function AuthDemoPage() {
  const { isAuthenticated, user } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <NetWizHeader />

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Authentication System Demo</h1>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Authentication Status */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Authentication Status</h2>

          {isAuthenticated ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-green-700 font-medium">Authenticated</span>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">User Information</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div><strong>Username:</strong> {user?.username}</div>
                  <div><strong>User Type:</strong> {user?.user_type}</div>
                  <div><strong>Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</div>
                  <div><strong>Member Since:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-red-700 font-medium">Not Authenticated</span>
              </div>

              <p className="text-gray-600">
                Sign in to access protected features and manage your account.
              </p>

              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Sign In / Sign Up
              </button>
            </div>
          )}
        </div>

        {/* Protected Content Demo */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Protected Content</h2>

          <ProtectedRoute
            fallback={
              <div className="text-center py-8">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <p className="text-gray-600 mb-4">This content requires authentication</p>
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Sign In to View
                </button>
              </div>
            }
          >
            <div className="text-center py-8">
              <div className="text-green-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome!</h3>
              <p className="text-gray-600 mb-4">
                You have successfully accessed protected content. This demonstrates that the authentication system is working correctly.
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 text-sm">
                  <strong>Features demonstrated:</strong>
                </p>
                <ul className="text-green-700 text-sm mt-2 space-y-1">
                  <li>• JWT token-based authentication</li>
                  <li>• Automatic token refresh</li>
                  <li>• Protected route components</li>
                  <li>• User session management</li>
                </ul>
              </div>
            </div>
          </ProtectedRoute>
        </div>
      </div>

      {/* User Profile Section */}
      {isAuthenticated && (
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Management</h2>
            <UserProfile />
          </div>
        </div>
      )}
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </div>
  )
}

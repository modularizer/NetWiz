/**
 * NetWiz Header Component
 *
 * Modular header component based on the existing NetWiz design.
 * Includes authentication controls and navigation.
 */

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { UserProfile, ChangePasswordForm } from '@/components/auth'
import VersionInfo from '@/components/VersionInfo'

interface NetWizHeaderProps {
  className?: string
}

export function NetWizHeader({ className = '' }: NetWizHeaderProps) {
  const { isAuthenticated, user, signout } = useAuth()
  const [showUserProfile, setShowUserProfile] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)


  const handleSignOut = async () => {
    try {
      await signout()
      setShowUserMenu(false)
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  return (
    <>
      <header className={`bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-300 px-6 py-5 ${className}`}>
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <img
              src={'./logo-full.svg'}
              alt="NetWiz Logo"
              className="h-12 w-auto"
            />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">NetWiz</h1>
              <p className="text-sm text-gray-500">PCB Netlist Visualizer + Validator</p>
            </div>
          </div>

          {/* Right side content */}
          <div className="flex items-center space-x-4">
            {/* Profile Icon */}
            <div className="flex items-center space-x-3">
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {/* Profile Icon */}
                  <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center border-2 border-gray-500">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span>{isAuthenticated ? user?.username : 'Profile'}</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    {isAuthenticated ? (
                      <>
                        <button
                          onClick={() => {
                            setShowUserProfile(true)
                            setShowUserMenu(false)
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Profile
                        </button>
                        <button
                          onClick={() => {
                            setShowChangePassword(true)
                            setShowUserMenu(false)
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Change Password
                        </button>
                        <button
                          onClick={handleSignOut}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Sign Out
                        </button>
                      </>
                    ) : (
                      <div className="px-4 py-2 text-sm text-gray-500">
                        Please sign in to access profile options
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Version Info */}
              <VersionInfo />
            </div>
          </div>
        </div>
      </header>

      {/* User Profile Modal */}
      {showUserProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">User Profile</h2>
              <button
                onClick={() => setShowUserProfile(false)}
                className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <UserProfile />
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      {showChangePassword && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Change Password</h2>
              <button
                onClick={() => setShowChangePassword(false)}
                className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <ChangePasswordForm onSuccess={() => setShowChangePassword(false)} />
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close user menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </>
  )
}

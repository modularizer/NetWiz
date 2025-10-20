/**
 * Protected Route Component
 *
 * Wraps components that require authentication.
 * Redirects to sign in if user is not authenticated.
 */

import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { AuthModal } from '@/components/auth'

interface ProtectedRouteProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Authentication Required</h1>
          <p className="text-gray-600 mb-6">Please sign in to access this page.</p>
          <AuthModal isOpen={true} onClose={() => {}} />
        </div>
      </div>
    )
  }

  return <>{children}</>
}

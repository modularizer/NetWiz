/**
 * Authenticated App Router
 *
 * Handles authentication state and shows appropriate content:
 * - SignInPage when not authenticated
 * - Main app routes when authenticated
 */

import { Routes, Route } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import NetlistPage from '@/pages/NetlistPage'
import { AuthDemoPage } from '@/pages/AuthDemoPage'
import { SignInPage } from '@/pages/SignInPage'

export function AuthenticatedAppRouter() {
  const { isAuthenticated, isLoading } = useAuth()

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Show sign-in page if not authenticated
  if (!isAuthenticated) {
    return <SignInPage />
  }

  // Show main app routes if authenticated
  return (
    <div className="h-screen flex flex-col">
      <Routes>
        <Route path="/" element={<NetlistPage />} />
        <Route path="/netlist" element={<NetlistPage />} />
        <Route path="/auth-demo" element={<AuthDemoPage />} />
        {/* Add more routes as needed */}
      </Routes>
    </div>
  )
}

/**
 * Sign In Page Component
 *
 * Full-page sign-in interface that replaces the main content
 * when users are not authenticated.
 */

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { SignInForm, SignUpForm } from '@/components/auth'
import { getCachedUsername, setCachedUsername } from '@/utils/authUtils'
import { NetWizInfo } from '@/components/NetWizInfo'

export function SignInPage() {
  const { clearError } = useAuth()
  const [mode, setMode] = useState<'signin' | 'signup'>('signup') // Default to signup
  const [isInitialized, setIsInitialized] = useState(false)

  // Check for cached username on mount
  useEffect(() => {
    const cachedUsername = getCachedUsername()
    if (cachedUsername) {
      setMode('signin')
    }
    setIsInitialized(true)
  }, [])

  const switchToSignUp = () => {
    setMode('signup')
    clearError()
  }

  const switchToSignIn = () => {
    setMode('signin')
    clearError()
  }

  const handleSuccess = () => {
    // Cache username when user successfully signs in
    const usernameInput = document.querySelector('input[name="username"]') as HTMLInputElement
    if (usernameInput?.value) {
      setCachedUsername(usernameInput.value)
    }
  }

  // Don't render until we've checked for cached username
  if (!isInitialized) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col lg:flex-row">
      {/* NetWiz Info - Left side on desktop, top on mobile */}
      <div className="lg:w-1/2 w-full lg:h-full h-1/2">
        <NetWizInfo />
      </div>

      {/* Authentication Form - Right side on desktop, bottom on mobile */}
      <div className="lg:w-1/2 w-full lg:h-full h-1/2 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-lg w-full">
          {mode === 'signin' ? (
            <SignInForm
              onSuccess={handleSuccess}
              onSwitchToSignUp={switchToSignUp}
            />
          ) : (
            <SignUpForm
              onSuccess={handleSuccess}
              onSwitchToSignIn={switchToSignIn}
            />
          )}
        </div>
      </div>
    </div>
  )
}

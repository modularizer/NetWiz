/**
 * Main App Component
 *
 * This is the root component of the NetWiz frontend application.
 * It sets up the routing, global state, and overall layout structure.
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { useState, useEffect, useRef, useCallback } from 'react'
import NetlistPage from '@/pages/NetlistPage'
import { BackendChecker } from '@/components/BackendChecker'
import { updateApiBaseUrl, DEFAULT_API_URL, API_URL_STORAGE_KEY } from '@/services/api'
import { BasePathProvider, useBasePath } from '@/contexts/BasePathContext'
import './styles/globals.css'

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

// Router component that uses base path context
const AppRouter: React.FC = () => {
  const { basePath } = useBasePath()

  // Convert base path to basename format for React Router
  // /NetWiz/ -> /NetWiz, / -> /
  const basename = basePath.endsWith('/') ? basePath.slice(0, -1) : basePath

  console.log('AppRouter: Using basename:', basename)

  return (
    <Router basename={basename}>
      <Routes>
        <Route path="/" element={<NetlistPage />} />
        <Route path="/netlist" element={<NetlistPage />} />
        {/* Add more routes as needed */}
      </Routes>
    </Router>
  )
}

function App() {
  const [backendAvailable, setBackendAvailable] = useState(false)
  const [isCheckingBackend, setIsCheckingBackend] = useState(true)
  const healthCheckIntervalRef = useRef<number | null>(null)

  const handleApiUrlChange = (newUrl: string) => {
    updateApiBaseUrl(newUrl)
  }

  const handleBackendStatusChange = (isAvailable: boolean) => {
    setBackendAvailable(isAvailable)
    setIsCheckingBackend(false)
  }

  // Health check function
  const performHealthCheck = useCallback(async () => {
    // Use cached API URL from localStorage, fallback to default
    const cachedUrl = localStorage.getItem(API_URL_STORAGE_KEY)
    const apiUrl = cachedUrl || DEFAULT_API_URL

    try {
      console.log('App: Performing health check at:', `${apiUrl}/`)
      const response = await fetch(`${apiUrl}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        const isNetWiz = data.message === 'PCB Netlist Visualizer + Validator'

        if (!isNetWiz) {
          console.log('App: Health check failed - not NetWiz backend')
          setBackendAvailable(false)
        }
        // If isNetWiz is true, keep backendAvailable as true
      } else {
        console.log('App: Health check failed - HTTP error:', response.status)
        setBackendAvailable(false)
      }
    } catch (error) {
      console.log('App: Health check failed - network error:', error)
      setBackendAvailable(false)
    }
  }, [])

  // Start health checks when backend becomes available
  useEffect(() => {
    if (backendAvailable) {
      console.log('App: Starting health checks every 5 seconds')
      healthCheckIntervalRef.current = window.setInterval(performHealthCheck, 5000)
    } else {
      // Stop health checks when backend is not available
      if (healthCheckIntervalRef.current) {
        console.log('App: Stopping health checks')
        window.clearInterval(healthCheckIntervalRef.current)
        healthCheckIntervalRef.current = null
      }
    }

    // Cleanup on unmount
    return () => {
      if (healthCheckIntervalRef.current) {
        window.clearInterval(healthCheckIntervalRef.current)
        healthCheckIntervalRef.current = null
      }
    }
  }, [backendAvailable, performHealthCheck])

  // Initial backend check
  useEffect(() => {
    const checkInitialBackend = async () => {
      console.log('App: Starting initial backend check')
      // Use cached API URL from localStorage, fallback to default
      const cachedUrl = localStorage.getItem(API_URL_STORAGE_KEY)
      const apiUrl = cachedUrl || DEFAULT_API_URL

      try {
        console.log('App: Checking backend at:', `${apiUrl}/`)
        const response = await fetch(`${apiUrl}/`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        })

        console.log('App: Backend response status:', response.status)

        if (response.ok) {
          const data = await response.json()
          console.log('App: Backend response data:', data)
          const isNetWiz = data.message === 'PCB Netlist Visualizer + Validator'
          console.log('App: Is NetWiz backend?', isNetWiz)

          if (isNetWiz) {
            console.log('App: Backend is available and is NetWiz')
            setBackendAvailable(true)
            setIsCheckingBackend(false)
            return
          }
        }

        console.log('App: Backend not available or not NetWiz')
        setBackendAvailable(false)
        setIsCheckingBackend(false)
      } catch (error) {
        console.log('App: Backend check failed:', error)
        setBackendAvailable(false)
        setIsCheckingBackend(false)
      }
    }

    checkInitialBackend()
  }, [])

  // Show loading state while checking backend
  if (isCheckingBackend) {
    return (
      <BasePathProvider>
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Checking backend connection...</p>
            </div>
          </div>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </BasePathProvider>
    )
  }

  // Show backend checker if backend is not available
  if (!backendAvailable) {
    return (
      <BasePathProvider>
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-6">
              <BackendChecker
                onApiUrlChange={handleApiUrlChange}
                onBackendStatusChange={handleBackendStatusChange}
              />
            </div>
          </div>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </BasePathProvider>
    )
  }

  // Show main app if backend is available
  return (
    <BasePathProvider>
      <QueryClientProvider client={queryClient}>
        <AppRouter />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </BasePathProvider>
  )
}

export default App

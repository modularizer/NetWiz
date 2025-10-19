/**
 * Main App Component
 *
 * This is the root component of the NetWiz frontend application.
 * It sets up the routing, global state, and overall layout structure.
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { useState, useEffect } from 'react'
import NetlistPage from '@/pages/NetlistPage'
import { BackendChecker } from '@/components/BackendChecker'
import { updateApiBaseUrl } from '@/services/api'
import { BasePathProvider } from '@/contexts/BasePathContext'
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

function App() {
  const [backendAvailable, setBackendAvailable] = useState(false)
  const [isCheckingBackend, setIsCheckingBackend] = useState(true)

  const handleApiUrlChange = (newUrl: string) => {
    updateApiBaseUrl(newUrl)
  }

  const handleBackendStatusChange = (isAvailable: boolean) => {
    setBackendAvailable(isAvailable)
    setIsCheckingBackend(false)
  }

  // Initial backend check
  useEffect(() => {
    const checkInitialBackend = async () => {
      console.log('App: Starting initial backend check')
      const defaultBackendPort = import.meta.env.VITE_BACKEND_PORT || '5000'
      const defaultApiUrl = `http://localhost:${defaultBackendPort}`

      try {
        console.log('App: Checking backend at:', `${defaultApiUrl}/`)
        const response = await fetch(`${defaultApiUrl}/`, {
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
        <Router>
          <Routes>
            <Route path="/" element={<NetlistPage />} />
            <Route path="/netlist" element={<NetlistPage />} />
            {/* Add more routes as needed */}
          </Routes>
        </Router>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </BasePathProvider>
  )
}

export default App

/**
 * Main App Component
 *
 * This is the root component of the NetWiz frontend application.
 * It sets up the routing, global state, and overall layout structure.
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { useEffect, useState } from 'react'
import NetlistPage from '@/pages/NetlistPage'
import { BackendChecker } from '@/components/BackendChecker'
import { updateApiBaseUrl } from '@/services/api'
import { saveBasePath } from '@/utils/basePath'
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

  // Detect and save the base path on app load
  useEffect(() => {
    saveBasePath()
  }, [])

  const handleApiUrlChange = (newUrl: string) => {
    updateApiBaseUrl(newUrl)
  }

  const handleBackendStatusChange = (isAvailable: boolean) => {
    setBackendAvailable(isAvailable)
    setIsCheckingBackend(false)
  }

  // Show loading state while checking backend
  if (isCheckingBackend) {
    return (
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Checking backend connection...</p>
          </div>
        </div>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    )
  }

  // Show backend checker if backend is not available
  if (!backendAvailable) {
    return (
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
    )
  }

  // Show main app if backend is available
  return (
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
  )
}

export default App

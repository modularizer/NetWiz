/**
 * Main App Component
 *
 * This is the root component of the NetWiz frontend application.
 * It sets up the routing, global state, and overall layout structure.
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { useEffect } from 'react'
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
  // Detect and save the base path on app load
  useEffect(() => {
    saveBasePath()
  }, [])

  const handleApiUrlChange = (newUrl: string) => {
    updateApiBaseUrl(newUrl)
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <div className="container mx-auto px-4 py-6">
            <BackendChecker onApiUrlChange={handleApiUrlChange} />
          </div>
          <Routes>
            <Route path="/" element={<NetlistPage />} />
            <Route path="/netlist" element={<NetlistPage />} />
            {/* Add more routes as needed */}
          </Routes>
        </div>
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App

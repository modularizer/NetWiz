import React, { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, Download } from 'lucide-react'

interface BackendStatus {
  accessible: boolean
  isNetWiz: boolean
  error?: string
}

interface BackendCheckerProps {
  onApiUrlChange: (url: string) => void
}

export const BackendChecker: React.FC<BackendCheckerProps> = ({ onApiUrlChange }) => {
  const [status, setStatus] = useState<BackendStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const defaultBackendPort = import.meta.env.VITE_BACKEND_PORT || '5000'
  const defaultApiUrl = `http://localhost:${defaultBackendPort}`

  // Load saved API URL from localStorage
  const [customApiUrl, setCustomApiUrl] = useState(() => {
    const saved = localStorage.getItem('netwiz-api-url')
    return saved || ''
  })

  useEffect(() => {
    // Use saved API URL if available, otherwise use default
    const apiUrl = customApiUrl || defaultApiUrl
    checkBackendStatus(apiUrl)
  }, [])

  const checkBackendStatus = async (apiUrl?: string) => {
    setLoading(true)
    const url = apiUrl || defaultApiUrl

    try {
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        const isNetWiz = data.app_name === 'NetWiz' || data.app_name === 'netwiz_backend'

        setStatus({
          accessible: true,
          isNetWiz,
        })
      } else {
        setStatus({
          accessible: false,
          isNetWiz: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        })
      }
    } catch (error) {
      setStatus({
        accessible: false,
        isNetWiz: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleApiUrlChange = (newUrl: string) => {
    setCustomApiUrl(newUrl)
    // Save to localStorage
    localStorage.setItem('netwiz-api-url', newUrl)
    onApiUrlChange(newUrl)
    checkBackendStatus(newUrl)
  }

  const getDockerInstructions = () => (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
      <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
        <Download className="w-4 h-4 mr-2" />
        Run Backend with Docker (No Source Code Required)
      </h3>
      <div className="text-sm text-gray-700 space-y-2">
        <p><strong>Option 1: One-liner (No file saved)</strong></p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          curl -s https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml | docker-compose -f - up -d
        </code>

        <p><strong>Option 1b: Download file first (if one-liner fails)</strong></p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          curl -O https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml && docker-compose -f docker-compose.prod.yml up -d
        </code>

        <p><strong>Option 2: Host the backend another way</strong></p>
        <p>See <a href="https://github.com/modularizer/NetWiz" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline">https://github.com/modularizer/NetWiz</a> for more information.</p>

        <div className="mt-3 p-2 bg-yellow-50 rounded text-xs text-yellow-800">
          <strong>⚠️ Docker Permission Error?</strong> If you get "Permission denied" errors:
          <br />• Run with sudo: <code className="bg-yellow-100 px-1 rounded">sudo docker-compose -f docker-compose.prod.yml up -d</code>
          <br />• Or add your user to docker group: <code className="bg-yellow-100 px-1 rounded">sudo usermod -aG docker $USER</code> (then logout/login)
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
          <span className="text-blue-800">Checking backend connection...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-300 px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img
              src="./logo-full.svg"
              alt="NetWiz Logo"
              className="h-12 w-auto"
            />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">NetWiz</h1>
              <p className="text-sm text-gray-500">PCB Netlist Visualizer + Validator</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="space-y-4">
          {/* Status Display */}
          <div className={`p-4 border rounded-lg ${
            status?.accessible && status?.isNetWiz
              ? 'bg-green-50 border-green-200'
              : 'bg-red-50 border-red-200'
          }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {status?.accessible && status?.isNetWiz ? (
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            )}
            <div>
              <h3 className="font-semibold text-gray-900">
                {status?.accessible && status?.isNetWiz
                  ? 'Backend Connected'
                  : 'Backend Not Available'
                }
              </h3>
              <p className="text-sm text-gray-600">
                {status?.accessible && status?.isNetWiz
                  ? 'NetWiz backend is running and accessible'
                  : status?.accessible
                    ? 'Backend is running but not NetWiz'
                    : `Cannot connect to backend: ${status?.error || 'Unknown error'}`
                }
              </p>
            </div>
          </div>

        </div>
      </div>


      {/* Instructions for when backend is not accessible */}
      {(!status?.accessible || !status?.isNetWiz) && (
        <div className="space-y-4">
          {getDockerInstructions()}

          {/* API URL Input */}
          <div className="p-4 border rounded-lg bg-gray-50">
            <h3 className="font-semibold text-gray-900 mb-3">Test Backend Connection</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Backend API URL
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={customApiUrl || defaultApiUrl}
                    onChange={(e) => setCustomApiUrl(e.target.value)}
                    placeholder={defaultApiUrl}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => handleApiUrlChange(customApiUrl || defaultApiUrl)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Verify
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Default: {defaultApiUrl} • Saved to browser storage
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
        </div>
      </div>
    </div>
  )
}

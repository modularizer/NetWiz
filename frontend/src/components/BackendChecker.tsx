import React, { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, Settings, Download } from 'lucide-react'

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
  const [customApiUrl, setCustomApiUrl] = useState('')
  const [showSettings, setShowSettings] = useState(false)

  const defaultBackendPort = import.meta.env.VITE_BACKEND_PORT || '5000'
  const defaultApiUrl = `http://localhost:${defaultBackendPort}`

  useEffect(() => {
    checkBackendStatus()
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
        <p><strong>Option 1: Download and run production compose file (Recommended)</strong></p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          curl -O https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml
        </code>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          docker-compose -f docker-compose.prod.yml up -d
        </code>

        <p><strong>Option 2: Run individual containers</strong></p>
        <p>1. Start MongoDB:</p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          docker run -d --name netwiz-mongodb -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password -p 27017:27017 mongo:7.0
        </code>

        <p>2. Start NetWiz Backend:</p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          docker run -d --name netwiz-backend -e MONGODB_URI=mongodb://admin:password@netwiz-mongodb:27017/netwiz?authSource=admin -e CORS_ORIGINS=https://modularizer.github.io,https://modularizer.github.io/NetWiz -p 5000:5000 --link netwiz-mongodb:mongodb ghcr.io/modularizer/netwiz-backend:latest
        </code>

        <p><strong>Option 3: If you have the source code</strong></p>
        <code className="block bg-gray-200 p-2 rounded text-xs">
          docker-compose up --build
        </code>

        <div className="mt-3 p-2 bg-blue-50 rounded text-xs text-blue-800">
          <strong>💡 Tip:</strong> Option 1 is the easiest - just download one file and run it!
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

          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center text-sm text-gray-600 hover:text-gray-800"
          >
            <Settings className="w-4 h-4 mr-1" />
            Settings
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-4 border rounded-lg bg-gray-50">
          <h3 className="font-semibold text-gray-900 mb-3">Backend Configuration</h3>

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
                  Test
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Default: {defaultApiUrl}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions for when backend is not accessible */}
      {(!status?.accessible || !status?.isNetWiz) && getDockerInstructions()}
    </div>
  )
}

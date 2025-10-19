import React, { useState, useEffect, useCallback, useRef } from 'react'
import { AlertCircle, CheckCircle, Download, Copy, Check } from 'lucide-react'
import { useBasePath } from '@/contexts/BasePathContext'
import { DEFAULT_API_URL, API_URL_STORAGE_KEY } from '@/services/api'

interface BackendStatus {
  accessible: boolean
  isNetWiz: boolean
  error?: string
}

interface BackendCheckerProps {
  onApiUrlChange: (url: string) => void
  onBackendStatusChange: (isAvailable: boolean) => void
}

export const BackendChecker: React.FC<BackendCheckerProps> = ({ onApiUrlChange, onBackendStatusChange }) => {
  const [status, setStatus] = useState<BackendStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const { withBasePath } = useBasePath()
  const defaultApiUrl = DEFAULT_API_URL

  // Auto-check state
  const [checkInterval, setCheckInterval] = useState(5000) // Start with 5 seconds
  const intervalRef = useRef<number | null>(null)
  const lastUserActionRef = useRef<number>(Date.now())

  // Load saved API URL from localStorage
  const [customApiUrl, setCustomApiUrl] = useState(() => {
    const saved = localStorage.getItem(API_URL_STORAGE_KEY)
    return saved || ''
  })

  const checkBackendStatus = useCallback(async (apiUrl?: string, isAutoCheck = false) => {
    if (isAutoCheck) {
      console.log('BackendChecker: Auto-checking backend...')
    } else {
      console.log('BackendChecker: Manual check with apiUrl =', apiUrl)
    }

    const url = apiUrl || customApiUrl || defaultApiUrl
    console.log('BackendChecker: Using URL =', url)

    try {
      const response = await fetch(`${url}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      console.log('BackendChecker: Response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('BackendChecker: Response data:', data)
        const isNetWiz = data.message === 'PCB Netlist Visualizer + Validator'
        console.log('BackendChecker: Is NetWiz?', isNetWiz)

        setStatus({
          accessible: true,
          isNetWiz,
        })

        // Notify parent component that backend is available
        if (isNetWiz) {
          console.log('BackendChecker: Notifying parent that backend is available')
          onBackendStatusChange(true)
          // Stop auto-checking when backend is found
          if (intervalRef.current) {
            window.clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      } else {
        console.log('BackendChecker: Response not OK:', response.status, response.statusText)
        setStatus({
          accessible: false,
          isNetWiz: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        })
        onBackendStatusChange(false)
      }
    } catch (error) {
      console.log('BackendChecker: Fetch error:', error)
      setStatus({
        accessible: false,
        isNetWiz: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      })
      onBackendStatusChange(false)
    } finally {
      if (!isAutoCheck) {
        setLoading(false)
      }
    }
  }, [defaultApiUrl, customApiUrl, onBackendStatusChange])

  // Reset check interval to fast (5s) after user actions
  const resetCheckInterval = useCallback(() => {
    console.log('BackendChecker: Resetting check interval to 5s due to user action')
    setCheckInterval(5000)
    lastUserActionRef.current = Date.now()
  }, [])

  // Auto-checking effect with decaying intervals
  useEffect(() => {
    // Only auto-check if backend is not available
    if (status?.accessible && status?.isNetWiz) {
      return
    }

    const startAutoCheck = () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current)
      }

      intervalRef.current = window.setInterval(() => {
        checkBackendStatus(undefined, true)

        // Decay the interval: 5s -> 10s -> 20s -> 30s -> 60s (max)
        setCheckInterval(prev => {
          const timeSinceLastAction = Date.now() - lastUserActionRef.current
          if (timeSinceLastAction < 10000) { // Less than 10s since last action
            return 5000 // Keep at 5s
          }

          const nextInterval = Math.min(prev * 1.5, 60000) // Cap at 60s
          console.log(`BackendChecker: Auto-check interval decaying to ${nextInterval}ms`)
          return nextInterval
        })
      }, checkInterval)
    }

    startAutoCheck()

    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [checkBackendStatus, checkInterval, status])

  // Initial check on mount
  useEffect(() => {
    const apiUrl = customApiUrl || defaultApiUrl
    console.log('BackendChecker: Initial check triggered')
    checkBackendStatus(apiUrl)
  }, [customApiUrl, defaultApiUrl, checkBackendStatus])

  const handleApiUrlChange = (newUrl: string) => {
    setCustomApiUrl(newUrl)
    // Save to localStorage
    localStorage.setItem(API_URL_STORAGE_KEY, newUrl)
    onApiUrlChange(newUrl)
    resetCheckInterval() // Reset to fast checking
    checkBackendStatus(newUrl)
  }

  const copyToClipboard = async (text: string) => {
    try {
      // Check if clipboard API is available
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000) // Reset after 2 seconds
        resetCheckInterval() // Reset to fast checking after copying
      } else {
        // Fallback for older browsers or non-HTTPS contexts
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()

        try {
          const successful = document.execCommand('copy')
          if (successful) {
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
            resetCheckInterval() // Reset to fast checking after copying
          } else {
            console.warn('Failed to copy text using fallback method')
          }
        } catch (err) {
          console.warn('Fallback copy failed:', err)
        } finally {
          document.body.removeChild(textArea)
        }
      }
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const oneliner = `COMPOSE_PROJECT_NAME=netwiz f=$(mktemp) && curl -fsSL https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml -o "$f" && trap 'docker-compose -p netwiz -f "$f" down --rmi all --volumes --remove-orphans; rm -f "$f"' EXIT && docker-compose -p netwiz -f "$f" up`

  const getDockerInstructions = () => (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
      <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
        <Download className="w-4 h-4 mr-2" />
        Run Backend with Docker (No Source Code Required)
      </h3>
      <div className="text-sm text-gray-700 space-y-2">
        <p><strong>Option 1: One-liner (No file saved)</strong></p>
        <div
          className="block bg-gray-200 p-2 rounded text-xs cursor-pointer hover:bg-gray-300 transition-colors relative group"
          onClick={() => copyToClipboard(oneliner)}
        >
          <code className="select-none">
              {oneliner}
          </code>
          <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {copied ? (
              <Check className="w-3 h-3 text-green-600" />
            ) : (
              <Copy className="w-3 h-3 text-gray-600" />
            )}
          </div>
          {copied && (
            <div className="absolute -top-8 right-0 bg-green-600 text-white text-xs px-2 py-1 rounded shadow-lg">
              Copied!
            </div>
          )}
        </div>

        <p><strong>Option 2: Host the backend another way</strong></p>
        <p>See <a href="https://github.com/modularizer/NetWiz" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline">https://github.com/modularizer/NetWiz</a> for more information.</p>

        <div className="mt-3 p-2 bg-yellow-50 rounded text-xs text-yellow-800">
          <strong>⚠️ Docker Permission Error?</strong>
          <br />• Add your user to docker group: <code className="bg-yellow-100 px-1 rounded">sudo usermod -aG docker $USER</code> then <code  className="bg-yellow-100 px-1 rounded">newgrp docker</code>
            <br />• Or run with sudo (not recommended)
        </div>
      </div>
    </div>
  )

  if (loading) {
    const currentUrl = customApiUrl || defaultApiUrl
    return (
      <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
          <div>
            <span className="text-blue-800">Checking backend connection...</span>
            <div className="text-xs text-blue-600 mt-1">
              Checking: <code className="bg-blue-100 px-1 rounded">{currentUrl}/</code>
            </div>
          </div>
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
              src={withBasePath('logo-full.svg')}
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

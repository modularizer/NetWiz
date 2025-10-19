/**
 * Version Info Component
 *
 * Displays version information for both frontend and backend
 * Shows git metadata, build info, and other version details
 */

import React, { useState, useEffect } from 'react'
import { Info, X, GitBranch, Calendar, Hash, Tag } from 'lucide-react'
import { useBasePath } from '@/contexts/BasePathContext'

interface FrontendVersion {
  commit_hash: string
  commit_short: string
  branch: string
  tag: string
  build_time: string
  build_ref: string
  build_sha: string
}

interface BackendVersion {
  message: string
  version: string
  author: string
  email: string
  license: string
  url: string
  status: string
  docs: string
  health: string
  environment: string
  git?: {
    commit_hash: string
    commit_short: string
    branch: string
    tag: string
    build_time: string
    build_ref: string
    build_sha: string
  }
}

interface VersionInfoProps {
  className?: string
}

const VersionInfo: React.FC<VersionInfoProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [frontendVersion, setFrontendVersion] = useState<FrontendVersion | null>(null)
  const [backendVersion, setBackendVersion] = useState<BackendVersion | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { withBasePath } = useBasePath()

  // Load frontend version info
  useEffect(() => {
    const loadFrontendVersion = async () => {
      try {
        const response = await fetch(withBasePath('version.json'))
        if (response.ok) {
          const data = await response.json()
          setFrontendVersion(data.frontend)
        }
      } catch (err) {
        console.warn('Failed to load frontend version info:', err)
      }
    }

    loadFrontendVersion()
  }, [withBasePath])

  // Load backend version info
  const loadBackendVersion = async () => {
    setLoading(true)
    setError(null)

    try {
      // Get the API base URL from localStorage or use default
      const cachedUrl = localStorage.getItem('netwiz_api_url')
      const apiUrl = cachedUrl || 'http://localhost:5000'

      const response = await fetch(`${apiUrl}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBackendVersion(data)
      } else {
        setError(`Backend not available (${response.status})`)
      }
    } catch (err) {
      setError('Failed to connect to backend')
    } finally {
      setLoading(false)
    }
  }

  const handleOpen = () => {
    setIsOpen(true)
    if (!backendVersion) {
      loadBackendVersion()
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString()
    } catch {
      return dateString
    }
  }

  const formatCommitHash = (hash: string) => {
    return hash ? `${hash.substring(0, 7)}...` : 'N/A'
  }

  return (
    <>
      {/* Version Icon Button */}
      <button
        onClick={handleOpen}
        className={`p-2 rounded-lg hover:bg-gray-200 transition-colors ${className}`}
        title="Version Information"
      >
        <Info className="w-5 h-5 text-gray-600" />
      </button>

      {/* Version Info Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Version Information</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-6">
                {/* Frontend Version */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Frontend
                  </h3>
                  {frontendVersion ? (
                    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center">
                          <Hash className="w-4 h-4 text-gray-500 mr-2" />
                          <span className="text-gray-600">Commit:</span>
                          <span className="ml-2 font-mono text-gray-900">
                            {formatCommitHash(frontendVersion.commit_hash)}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <GitBranch className="w-4 h-4 text-gray-500 mr-2" />
                          <span className="text-gray-600">Branch:</span>
                          <span className="ml-2 font-mono text-gray-900">
                            {frontendVersion.branch || 'N/A'}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <Tag className="w-4 h-4 text-gray-500 mr-2" />
                          <span className="text-gray-600">Tag:</span>
                          <span className="ml-2 font-mono text-gray-900">
                            {frontendVersion.tag || 'N/A'}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                          <span className="text-gray-600">Built:</span>
                          <span className="ml-2 text-gray-900">
                            {formatDate(frontendVersion.build_time)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-4 text-gray-500 text-sm">
                      Frontend version information not available
                    </div>
                  )}
                </div>

                {/* Backend Version */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Backend
                  </h3>
                  {loading ? (
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      <span className="text-gray-600 text-sm">Loading backend info...</span>
                    </div>
                  ) : error ? (
                    <div className="bg-red-50 rounded-lg p-4 text-red-700 text-sm">
                      {error}
                    </div>
                  ) : backendVersion ? (
                    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Version:</span>
                          <span className="ml-2 font-mono text-gray-900">
                            {backendVersion.version}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Environment:</span>
                          <span className="ml-2 text-gray-900">
                            {backendVersion.environment}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Author:</span>
                          <span className="ml-2 text-gray-900">
                            {backendVersion.author}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Status:</span>
                          <span className="ml-2 text-gray-900">
                            {backendVersion.status}
                          </span>
                        </div>
                      </div>

                      {/* Backend Git Info */}
                      {backendVersion.git && (
                        <div className="border-t border-gray-200 pt-3 mt-3">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Git Information</h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="flex items-center">
                              <Hash className="w-4 h-4 text-gray-500 mr-2" />
                              <span className="text-gray-600">Commit:</span>
                              <span className="ml-2 font-mono text-gray-900">
                                {formatCommitHash(backendVersion.git.commit_hash)}
                              </span>
                            </div>
                            <div className="flex items-center">
                              <GitBranch className="w-4 h-4 text-gray-500 mr-2" />
                              <span className="text-gray-600">Branch:</span>
                              <span className="ml-2 font-mono text-gray-900">
                                {backendVersion.git.branch || 'N/A'}
                              </span>
                            </div>
                            <div className="flex items-center">
                              <Tag className="w-4 h-4 text-gray-500 mr-2" />
                              <span className="text-gray-600">Tag:</span>
                              <span className="ml-2 font-mono text-gray-900">
                                {backendVersion.git.tag || 'N/A'}
                              </span>
                            </div>
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                              <span className="text-gray-600">Built:</span>
                              <span className="ml-2 text-gray-900">
                                {formatDate(backendVersion.git.build_time)}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-4 text-gray-500 text-sm">
                      Backend version information not available
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default VersionInfo

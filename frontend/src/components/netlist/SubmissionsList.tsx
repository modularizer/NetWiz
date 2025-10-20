/**
 * Submissions List Component
 *
 * Displays a scrollable list of netlist submissions with compact single-line items.
 * Shows filename, timestamp, error count, warning count, and username (for admins).
 * Allows selection to load submission data into the editor.
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Clock, FileText, AlertCircle, AlertTriangle, User } from 'lucide-react'
import { apiClient } from '@/services/api'
import type { NetlistSubmission } from '@/types/netlist'

interface SubmissionsListProps {
  onSubmissionSelect: (submission: NetlistSubmission) => void
  selectedSubmissionId?: string
  isAdmin?: boolean
  refreshTrigger?: number // Add refresh trigger prop
}

interface SubmissionListItem {
  submission: NetlistSubmission
  username?: string
}

const SubmissionsList: React.FC<SubmissionsListProps> = ({
  onSubmissionSelect,
  selectedSubmissionId,
  isAdmin = false,
  refreshTrigger
}) => {
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [usernames, setUsernames] = useState<Record<string, string>>({})
  const [loadingUsernames, setLoadingUsernames] = useState<Set<string>>(new Set())

  // Function to fetch username for a user ID
  const fetchUsername = useCallback(async (userId: string) => {
    if (usernames[userId] || loadingUsernames.has(userId)) {
      return // Already have it or currently loading
    }

    setLoadingUsernames(prev => new Set(prev).add(userId))

    try {
      const user = await apiClient.getUserById(userId)
      setUsernames(prev => ({ ...prev, [userId]: user.username }))
    } catch (error) {
      console.error(`Failed to fetch username for user ${userId}:`, error)
      setUsernames(prev => ({ ...prev, [userId]: 'Unknown User' }))
    } finally {
      setLoadingUsernames(prev => {
        const newSet = new Set(prev)
        newSet.delete(userId)
        return newSet
      })
    }
  }, [usernames, loadingUsernames])

  // Effect to update submissions when usernames change
  useEffect(() => {
    setSubmissions(prev => prev.map(item => ({
      ...item,
      username: item.submission.user_id ? usernames[item.submission.user_id] || 'Loading...' : 'Unknown User'
    })))
  }, [usernames])

  // Effect to refresh submissions when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger !== undefined) {
      setPage(1)
      setSubmissions([])
      loadSubmissions(1, false)
    }
  }, [refreshTrigger])

  const loadSubmissions = async (pageNum: number = 1, append: boolean = false) => {
    try {
      setLoading(true)
      setError(null)

      const params: any = {
        page: pageNum,
        page_size: 20
      }

      // If admin, load all submissions
      if (isAdmin) {
        params.list_all = true
      }

      const response = await apiClient.listNetlists(params)

      if (!response || !response.submissions) {
        throw new Error('Invalid response from server')
      }

      const newSubmissions = response.submissions.map(submission => {
        if (!submission) {
          console.warn('Null submission in response:', submission)
          return null
        }

        // Trigger username fetching if we don't have it yet
        if (submission.user_id && !usernames[submission.user_id] && !loadingUsernames.has(submission.user_id)) {
          fetchUsername(submission.user_id)
        }

        return {
          submission: {
            ...submission,
            user_id: submission.user_id ?? null,
            filename: submission.filename ?? null,
            validation_result: submission.validation_result ?? null,
            netlist: submission.netlist ?? null
          } as NetlistSubmission,
          username: submission.user_id ? usernames[submission.user_id] || 'Loading...' : 'Unknown User'
        }
      }).filter(Boolean) as SubmissionListItem[]

      if (append) {
        setSubmissions(prev => [...prev, ...newSubmissions])
      } else {
        setSubmissions(newSubmissions)
      }

      setHasMore(newSubmissions.length === 20) // If we got a full page, there might be more
    } catch (err: any) {
      console.error('Failed to load submissions:', err)
      setError(err.message || 'Failed to load submissions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSubmissions(1, false)
  }, [isAdmin])

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      loadSubmissions(nextPage, true)
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const getErrorCount = (submission: NetlistSubmission) => {
    return submission.validation_result?.errors?.length || 0
  }

  const getWarningCount = (submission: NetlistSubmission) => {
    return submission.validation_result?.warnings?.length || 0
  }

  const handleSubmissionClick = async (submissionId: string) => {
    try {
      const submission = await apiClient.getNetlist(submissionId)

      if (!submission) {
        throw new Error('Invalid response from server')
      }

      onSubmissionSelect(submission)
    } catch (err: any) {
      console.error('Failed to load submission:', err)
      setError(err.message || 'Failed to load submission')
    }
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-600">
        <AlertCircle className="w-6 h-6 mx-auto mb-2" />
        <p className="text-sm">{error}</p>
        <button
          onClick={() => loadSubmissions(1, false)}
          className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-1.5 border-b border-gray-200 bg-gray-50">
        <h3 className="text-xs font-medium text-gray-900">
          {isAdmin ? 'All Submissions' : 'My Submissions'}
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto min-h-0">
        {submissions.length === 0 && !loading ? (
          <div className="p-2 text-center text-gray-500">
            <FileText className="w-5 h-5 mx-auto mb-1 opacity-50" />
            <p className="text-xs">No submissions</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {submissions.map((item) => {
              const { submission } = item
              const isSelected = selectedSubmissionId === submission.id
              const errorCount = getErrorCount(submission)
              const warningCount = getWarningCount(submission)

              return (
                <div
                  key={submission.id}
                  onClick={() => handleSubmissionClick(submission.id)}
                  className={`p-1.5 cursor-pointer hover:bg-gray-50 transition-colors ${
                    isSelected ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
                  }`}
                >
                  <div className="space-y-0.5">
                    {/* Filename */}
                    <div className="flex items-center space-x-1">
                      <FileText className="w-2.5 h-2.5 text-gray-400 flex-shrink-0" />
                      <span className="text-xs font-medium text-gray-900 truncate">
                        {submission.filename || 'Unnamed'}
                      </span>
                    </div>

                    {/* Username and timestamp */}
                    <div className="flex items-center justify-between">
                      {item.username && (
                        <div className="flex items-center space-x-1">
                          <User className="w-2 h-2 text-gray-400" />
                          <span className="text-xs text-gray-500 truncate max-w-16">
                            {item.username}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        <Clock className="w-2 h-2" />
                        <span>{formatTimestamp(submission.submission_timestamp)}</span>
                      </div>
                    </div>

                    {/* Status indicators */}
                    <div className="flex items-center space-x-2">
                      {errorCount > 0 && (
                        <div className="flex items-center space-x-1 text-xs text-red-600">
                          <AlertCircle className="w-2 h-2" />
                          <span>{errorCount}</span>
                        </div>
                      )}
                      {warningCount > 0 && (
                        <div className="flex items-center space-x-1 text-xs text-yellow-600">
                          <AlertTriangle className="w-2 h-2" />
                          <span>{warningCount}</span>
                        </div>
                      )}
                      {errorCount === 0 && warningCount === 0 && (
                        <div className="flex items-center space-x-1 text-xs text-green-600">
                          <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                          <span>✓</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {hasMore && (
          <div className="p-3 border-t border-gray-100">
            <button
              onClick={handleLoadMore}
              disabled={loading}
              className="w-full px-3 py-2 text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded transition-colors disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load More'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default SubmissionsList

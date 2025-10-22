/**
 * Main Netlist Page Component
 *
 * This is the primary page of the NetWiz application, featuring:
 * - Split-pane layout with JSON editor and graph visualization
 * - Real-time validation with error/warning display
 * - File upload and netlist management
 * - Interactive schematic visualization
 */

import React, { useState, useCallback, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { AlertCircle, CheckCircle, Loader2, Upload } from 'lucide-react'
import JsonEditor from '@/components/netlist/JsonEditor'
import GraphVisualization from '@/components/netlist/GraphVisualization'
import ValidationPanel from '@/components/netlist/ValidationPanel'
import SubmissionsList from '@/components/netlist/SubmissionsList'
import { NetWizHeader } from '@/components/layout/NetWizHeader'
import { useNetlistUpload } from '@/hooks'
import { useAuth } from '@/contexts/AuthContext'
import { testExamples, type TestExample } from '@/utils/testExamples'
import type { Netlist, ValidationResult, NetlistSubmission } from '@/types/netlist'

const NetlistPage: React.FC = () => {
  const [netlist, setNetlist] = useState<Netlist | null>(null)
  const [jsonText, setJsonText] = useState<string>('')
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [currentFilename, setCurrentFilename] = useState<string>('')
  const [selectedExample, setSelectedExample] = useState<string>('')
  const [netlistName, setNetlistName] = useState<string>('')
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<string>('')
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0)
  const [isSmallScreen, setIsSmallScreen] = useState(false)

  // Custom hooks for API operations
  const { uploadNetlist, isUploading } = useNetlistUpload()
  const { user } = useAuth()

  // Responsive layout detection
  useEffect(() => {
    const checkScreenSize = () => {
      setIsSmallScreen(window.innerWidth < 1024) // lg breakpoint
    }

    checkScreenSize()
    window.addEventListener('resize', checkScreenSize)

    return () => window.removeEventListener('resize', checkScreenSize)
  }, [])

  // Navigation handler for clicking on validation errors
  const handleNavigateToError = useCallback((lineNumber: number, characterPosition: number) => {
    console.log('NetlistPage: handleNavigateToError called with:', lineNumber, characterPosition)
    // Call the Monaco Editor navigation function directly
    if ((window as any).navigateToJsonError) {
      console.log('NetlistPage: Calling Monaco navigation function')
      ;(window as any).navigateToJsonError(lineNumber, characterPosition)
    } else {
      console.log('NetlistPage: Monaco navigation function not found')
    }
  }, [])

  // Handle JSON text changes from editor
  const handleJsonTextChange = useCallback(async (newJsonText: string) => {
    console.log('Handling JSON text change, length:', newJsonText.length)
    setJsonText(newJsonText)

    // Try to parse JSON for the netlist state (for graph visualization)
    try {
      const parsed = JSON.parse(newJsonText)
      setNetlist(parsed)
    } catch (error) {
      // Invalid JSON - clear netlist but keep text
      setNetlist(null)
    }
  }, [])

  // Handle file upload - only load content, no auto-validation or upload
  const handleFileUpload = useCallback(async (file: File) => {
    try {
      const text = await file.text()
      setJsonText(text)
      setCurrentFilename(file.name)
      setSelectedExample('') // Reset example selection when file is uploaded

      // Clear previous validation results when loading new content
      setValidationResult(null)

      // Auto-populate netlist name from filename
      const nameWithoutExtension = file.name.replace(/\.[^/.]+$/, '')
      setNetlistName(nameWithoutExtension)

      // Try to parse for netlist state
      try {
        const parsed = JSON.parse(text)
        setNetlist(parsed)
      } catch (error) {
        setNetlist(null)
      }

      // Note: No automatic validation or upload - user must click validate manually
    } catch (error) {
      console.error('File load error:', error)
    }
  }, [])

  const handleTestExampleSelect = useCallback(async (example: TestExample) => {
    try {
      // Fetch the static test example file from the public directory
      const response = await fetch(`./test-examples/${example.filename}`)
      if (!response.ok) {
        throw new Error(`Failed to load test example: ${response.statusText}`)
      }
      const text = await response.text()

      setJsonText(text)
      setCurrentFilename(example.filename)

      // Clear previous validation results when loading new content
      setValidationResult(null)

      // Auto-populate netlist name from example name
      setNetlistName(example.name)

      // Parse the JSON to update netlist state (this derives from the JSON)
      try {
        const parsed = JSON.parse(text)
        setNetlist(parsed)
      } catch (error) {
        setNetlist(null)
      }
    } catch (error) {
      console.error('Error loading test example:', error)
    }
  }, [])

  // Handle submission selection from the list
  const handleSubmissionSelect = useCallback((submission: NetlistSubmission) => {
    if (!submission) {
      console.error('NetlistPage: submission is undefined!')
      return
    }

    console.log('Loading submission:', submission.id)

    // The JSON content is the source of truth - load it first
    setJsonText(submission.json_text)

    // Update filename to reflect what we're looking at
    setCurrentFilename(submission.filename || 'Unnamed')
    setNetlistName(submission.filename?.replace(/\.[^/.]+$/, '') || 'Unnamed')
    setSelectedSubmissionId(submission.id)

    // Reset example selection since we're loading a submission
    setSelectedExample('')

    // Parse the JSON to update netlist state (this derives from the JSON)
    try {
      const parsed = JSON.parse(submission.json_text)
      setNetlist(parsed)
    } catch (error) {
      console.error('Failed to parse submission JSON:', error)
      setNetlist(null)
    }

    // Load the stored validation results (these are already computed and stored)
    setValidationResult(submission.validation_result)
  }, [])

  const handleValidate = useCallback(async () => {
    if (!jsonText) return

    try {
      // Create a file object from the JSON text
      const blob = new Blob([jsonText], { type: 'application/json' })
      // Use the manually entered netlistName as the filename, with fallbacks
      let filename = netlistName || currentFilename || 'netlist.json'

      // Ensure filename has .json extension
      if (!filename.toLowerCase().endsWith('.json')) {
        filename = filename + '.json'
      }

      const file = new File([blob], filename, { type: 'application/json' })

      // Upload to server
      const result = await uploadNetlist({
        file,
        filename: filename
      })

      console.log('Upload successful:', result)

      // The upload result includes validation, so we can use that
      if (result && result.validation_result) {
        setValidationResult(result.validation_result)
        console.log('Validation result set:', result.validation_result)

        // Trigger refresh of submissions list
        setRefreshTrigger(prev => prev + 1)
      } else {
        console.warn('No validation result in upload response:', result)
      }
    } catch (error) {
      console.error('Upload/validation error:', error)

      // Set a generic error validation result
      setValidationResult({
        is_valid: false,
        errors: [{
          message: error instanceof Error ? error.message : 'Upload failed',
          error_type: {
            name: 'upload_error',
            description: 'An error occurred during upload'
          },
          severity: 'error',
          location: null
        }],
        warnings: [],
        validation_timestamp: new Date().toISOString(),
        validation_rules_applied: []
      })
    }
  }, [jsonText, currentFilename, netlistName, uploadNetlist])

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <NetWizHeader />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {isSmallScreen ? (
          // Mobile/Tablet Layout - Vertical Stack
          <PanelGroup direction="vertical">
            {/* Top Panel - Submissions List */}
            <Panel defaultSize={20} minSize={15} maxSize={30}>
              <SubmissionsList
                onSubmissionSelect={handleSubmissionSelect}
                selectedSubmissionId={selectedSubmissionId}
                isAdmin={user?.user_type === 'admin'}
                refreshTrigger={refreshTrigger}
              />
            </Panel>

            <PanelResizeHandle className="h-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

            {/* Middle Panel - JSON Editor */}
            <Panel defaultSize={50} minSize={30}>
              <div className="flex flex-col h-full overflow-hidden">
                <div className="bg-white border-b border-gray-200 px-4 py-2">
                  {/* Desktop Layout - Single Row */}
                  <div className="hidden lg:flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                      {currentFilename && (
                        <span className="text-xs text-gray-500">({currentFilename})</span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={netlistName}
                        onChange={(e) => setNetlistName(e.target.value)}
                        placeholder="Netlist name"
                        className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        onClick={handleValidate}
                        disabled={!jsonText || isUploading}
                        className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Validate and upload netlist"
                      >
                        {isUploading ? (
                          <Loader2 className="w-4 h-4 text-white animate-spin" />
                        ) : (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                        <span className="text-sm text-white">Validate</span>
                      </button>
                    </div>
                  </div>

                  {/* Mobile/Tablet Layout - Multiple Rows */}
                  <div className="lg:hidden space-y-2">
                    {/* Row 1: Title and Filename */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                        {currentFilename && (
                          <span className="text-xs text-gray-500">({currentFilename})</span>
                        )}
                      </div>
                    </div>

                    {/* Row 2: Controls */}
                    <div className="flex items-center justify-between space-x-2">
                      <input
                        type="text"
                        value={netlistName}
                        onChange={(e) => setNetlistName(e.target.value)}
                        placeholder="Netlist name"
                        className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <button
                        onClick={handleValidate}
                        disabled={!jsonText || isUploading}
                        className="flex items-center space-x-1 px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Validate and upload netlist"
                      >
                        {isUploading ? (
                          <Loader2 className="w-4 h-4 text-white animate-spin" />
                        ) : (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                        <span className="text-xs text-white">Validate</span>
                      </button>
                    </div>
                  </div>
                </div>
                <div className="flex-1 min-h-0">
                  <JsonEditor
                    value={jsonText}
                    onChange={handleJsonTextChange}
                    validationResult={validationResult}
                    onNavigateToError={handleNavigateToError}
                  />
                </div>
              </div>
            </Panel>

            <PanelResizeHandle className="h-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

            {/* Bottom Panel - Validation and Graph */}
            <Panel defaultSize={30} minSize={20}>
              <PanelGroup direction="vertical">
                {/* Validation Panel */}
                <Panel defaultSize={60} minSize={40}>
                  <div className="flex flex-col h-full overflow-hidden">
                    <div className="bg-white border-b border-gray-200 px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <h2 className="text-sm font-medium text-gray-900">Validation</h2>
                        {validationResult && (
                          <div className="flex items-center space-x-1">
                            {validationResult.is_valid ? (
                              <CheckCircle className="w-4 h-4 text-success-500" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-error-500" />
                            )}
                            <span className={`text-xs font-medium ${
                              validationResult.is_valid ? 'text-success-600' : 'text-error-600'
                            }`}>
                              {validationResult.is_valid ? 'Valid' : 'Invalid'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex-1 min-h-0">
                      <ValidationPanel
                        validationResult={validationResult}
                        onNavigateToError={handleNavigateToError}
                      />
                    </div>
                  </div>
                </Panel>

                <PanelResizeHandle className="h-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

                {/* Graph Visualization */}
                <Panel defaultSize={40} minSize={30}>
                  <div className="flex flex-col h-full overflow-hidden">
                    <div className="bg-white border-b border-gray-200 px-4 py-2 flex-shrink-0">
                      <h2 className="text-sm font-medium text-gray-900">Schematic</h2>
                    </div>
                    <div className="flex-1 min-h-0">
                      <GraphVisualization netlist={netlist} validationResult={validationResult} />
                    </div>
                  </div>
                </Panel>
              </PanelGroup>
            </Panel>
          </PanelGroup>
        ) : (
          // Desktop Layout - Horizontal Columns
          <PanelGroup direction="horizontal">
          {/* Left Panel - Submissions List */}
          <Panel defaultSize={15} minSize={12}>
            <SubmissionsList
              onSubmissionSelect={handleSubmissionSelect}
              selectedSubmissionId={selectedSubmissionId}
              isAdmin={user?.user_type === 'admin'}
              refreshTrigger={refreshTrigger}
            />
          </Panel>

          <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

          {/* Middle Panel - JSON Editor and Validation */}
          <Panel defaultSize={50} minSize={35}>
            <PanelGroup direction="vertical">
              {/* JSON Editor */}
              <Panel defaultSize={60} minSize={30}>
                <div className="flex flex-col h-full overflow-hidden">
                  <div className="bg-white border-b border-gray-200 px-4 py-2">
                    {/* Desktop Layout - Single Row */}
                    <div className="hidden xl:flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                        {currentFilename && (
                          <span className="text-xs text-gray-500">({currentFilename})</span>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {/* Netlist Name Input */}
                        <input
                          type="text"
                          value={netlistName}
                          onChange={(e) => setNetlistName(e.target.value)}
                          placeholder="Netlist name"
                          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                        <select
                          value={selectedExample}
                          onChange={(e) => {
                            setSelectedExample(e.target.value)
                            const example = testExamples.find(ex => ex.id === e.target.value)
                            if (example) {
                              handleTestExampleSelect(example)
                            }
                          }}
                          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="">Load example...</option>
                          {testExamples.map((example) => (
                            <option key={example.id} value={example.id}>
                              {example.name} ({example.category})
                            </option>
                          ))}
                        </select>
                        <input
                          type="file"
                          accept=".json"
                          onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) {
                              handleFileUpload(file)
                            }
                          }}
                          className="hidden"
                          id="file-upload"
                        />
                        <label
                          htmlFor="file-upload"
                          className="cursor-pointer p-1 rounded hover:bg-gray-100 transition-colors"
                          title="Upload JSON file"
                        >
                          <Upload className="w-4 h-4 text-gray-500" />
                        </label>
                        <button
                          onClick={handleValidate}
                          disabled={!jsonText || isUploading}
                          className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Validate and upload netlist"
                        >
                          {isUploading ? (
                            <Loader2 className="w-4 h-4 text-white animate-spin" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-white" />
                          )}
                          <span className="text-sm text-white">Validate</span>
                        </button>
                      </div>
                    </div>

                    {/* Tablet Layout - Two Rows */}
                    <div className="hidden lg:block xl:hidden space-y-2">
                      {/* Row 1: Title and Filename */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                          {currentFilename && (
                            <span className="text-xs text-gray-500">({currentFilename})</span>
                          )}
                        </div>
                      </div>

                      {/* Row 2: Controls */}
                      <div className="flex items-center justify-between space-x-2">
                        <input
                          type="text"
                          value={netlistName}
                          onChange={(e) => setNetlistName(e.target.value)}
                          placeholder="Netlist name"
                          className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                        <select
                          value={selectedExample}
                          onChange={(e) => {
                            setSelectedExample(e.target.value)
                            const example = testExamples.find(ex => ex.id === e.target.value)
                            if (example) {
                              handleTestExampleSelect(example)
                            }
                          }}
                          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="">Load example...</option>
                          {testExamples.map((example) => (
                            <option key={example.id} value={example.id}>
                              {example.name} ({example.category})
                            </option>
                          ))}
                        </select>
                        <input
                          type="file"
                          accept=".json"
                          onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) {
                              handleFileUpload(file)
                            }
                          }}
                          className="hidden"
                          id="file-upload-lg"
                        />
                        <label
                          htmlFor="file-upload-lg"
                          className="cursor-pointer p-1 rounded hover:bg-gray-100 transition-colors"
                          title="Upload JSON file"
                        >
                          <Upload className="w-4 h-4 text-gray-500" />
                        </label>
                        <button
                          onClick={handleValidate}
                          disabled={!jsonText || isUploading}
                          className="flex items-center space-x-1 px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Validate and upload netlist"
                        >
                          {isUploading ? (
                            <Loader2 className="w-4 h-4 text-white animate-spin" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-white" />
                          )}
                          <span className="text-xs text-white">Validate</span>
                        </button>
                      </div>
                    </div>

                    {/* Mobile Layout - Multiple Rows */}
                    <div className="lg:hidden space-y-2">
                      {/* Row 1: Title and Filename */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                          {currentFilename && (
                            <span className="text-xs text-gray-500">({currentFilename})</span>
                          )}
                        </div>
                      </div>

                      {/* Row 2: Netlist Name */}
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={netlistName}
                          onChange={(e) => setNetlistName(e.target.value)}
                          placeholder="Netlist name"
                          className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>

                      {/* Row 3: Controls */}
                      <div className="flex items-center justify-between space-x-2">
                        <select
                          value={selectedExample}
                          onChange={(e) => {
                            setSelectedExample(e.target.value)
                            const example = testExamples.find(ex => ex.id === e.target.value)
                            if (example) {
                              handleTestExampleSelect(example)
                            }
                          }}
                          className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="">Load example...</option>
                          {testExamples.map((example) => (
                            <option key={example.id} value={example.id}>
                              {example.name} ({example.category})
                            </option>
                          ))}
                        </select>
                        <input
                          type="file"
                          accept=".json"
                          onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) {
                              handleFileUpload(file)
                            }
                          }}
                          className="hidden"
                          id="file-upload-mobile"
                        />
                        <label
                          htmlFor="file-upload-mobile"
                          className="cursor-pointer p-1 rounded hover:bg-gray-100 transition-colors"
                          title="Upload JSON file"
                        >
                          <Upload className="w-4 h-4 text-gray-500" />
                        </label>
                        <button
                          onClick={handleValidate}
                          disabled={!jsonText || isUploading}
                          className="flex items-center space-x-1 px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Validate and upload netlist"
                        >
                          {isUploading ? (
                            <Loader2 className="w-4 h-4 text-white animate-spin" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-white" />
                          )}
                          <span className="text-xs text-white">Validate</span>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 min-h-0">
                    <JsonEditor
                      value={jsonText}
                      onChange={handleJsonTextChange}
                      validationResult={validationResult}
                      onNavigateToError={handleNavigateToError}
                    />
                  </div>
                </div>
              </Panel>

              <PanelResizeHandle className="h-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

              {/* Validation Panel */}
              <Panel defaultSize={40} minSize={20}>
                <div className="flex flex-col h-full overflow-hidden">
                  <div className="bg-white border-b border-gray-200 px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <h2 className="text-sm font-medium text-gray-900">Validation Results</h2>
                      {validationResult && (
                        <div className="flex items-center space-x-1">
                          {validationResult.is_valid ? (
                            <CheckCircle className="w-4 h-4 text-success-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-error-500" />
                          )}
                          <span className={`text-xs font-medium ${
                            validationResult.is_valid ? 'text-success-600' : 'text-error-600'
                          }`}>
                            {validationResult.is_valid ? 'Valid' : 'Invalid'}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex-1 min-h-0">
                    <ValidationPanel
                      validationResult={validationResult}
                      onNavigateToError={handleNavigateToError}
                    />
                  </div>
                </div>
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

          {/* Right Panel - Graph Visualization */}
          <Panel defaultSize={35} minSize={20} maxSize={50}>
            <div className="flex flex-col h-full overflow-hidden">
              <div className="bg-white border-b border-gray-200 px-4 py-2 flex-shrink-0">
                <h2 className="text-sm font-medium text-gray-900">Schematic Visualization</h2>
              </div>
              <div className="flex-1 min-h-0">
                <GraphVisualization netlist={netlist} validationResult={validationResult} />
              </div>
            </div>
          </Panel>
        </PanelGroup>
        )}
      </div>
    </div>
  )
}

export default NetlistPage

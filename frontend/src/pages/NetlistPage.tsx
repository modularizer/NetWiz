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
import { useNetlistValidation } from '@/hooks'
import { testExamples, type TestExample } from '@/utils/testExamples'
import type { Netlist, ValidationResult } from '@/types/netlist'

const NetlistPage: React.FC = () => {
  const [netlist, setNetlist] = useState<Netlist | null>(null)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)

  // Custom hooks for API operations
  const { validateNetlist, isValidating, validationResult: hookValidationResult } = useNetlistValidation()

  // Sync hook validation result with local state
  useEffect(() => {
    console.log('Hook validation result changed:', hookValidationResult, hookValidationResult?.errors)
    if (hookValidationResult) {
      setValidationResult(hookValidationResult)
    }
  }, [hookValidationResult])

  // Handle netlist changes from JSON editor
  const handleNetlistChange = useCallback(async (newNetlist: Netlist) => {
    console.log('Handling netlist change:', newNetlist)
    setNetlist(newNetlist)
    // Trigger validation - the hook will handle both success and error cases
    try {
      console.log('Calling validateNetlist...')
      await validateNetlist(newNetlist)
      console.log('validateNetlist completed')
    } catch (error) {
      console.error('Error in handleNetlistChange:', error)
    }
  }, [validateNetlist])

  // Handle file upload
  const handleFileUpload = useCallback(async (file: File) => {
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      setNetlist(parsed)
      // Trigger validation - the hook will handle both success and error cases
      await validateNetlist(parsed)
    } catch (error) {
      console.error('Upload error:', error)
      // Don't clear validation result - the hook should have handled the error
      // and returned a validation result if it was a validation error
    }
  }, [validateNetlist])

  // Manual validation test
  const handleManualValidation = useCallback(async () => {
    if (!netlist) return
    console.log('Manual validation triggered for:', netlist)
    try {
      await validateNetlist(netlist)
    } catch (error) {
      console.error('Manual validation error:', error)
    }
  }, [netlist, validateNetlist])
  const handleTestExampleSelect = useCallback(async (example: TestExample) => {
    try {
      const response = await fetch(`/test-examples/${example.filename}`)
      const text = await response.text()
      const parsed = JSON.parse(text)
      setNetlist(parsed)

      // Validate the loaded example
      const result = await validateNetlist(parsed)
      setValidationResult(result)
    } catch (error) {
      console.error('Error loading test example:', error)
      // Set a simple error validation result
      setValidationResult({
        is_valid: false,
        errors: [{
          message: 'Unhandled exception',
          error_type: 'validation_error',
          line_number: null,
          character_position: null
        }],
        warnings: [],
        applied_rules: []
      })
    }
  }, [validateNetlist])

  // Handle manual validation trigger
  const handleValidate = useCallback(async () => {
    if (!netlist) return

    try {
      const result = await validateNetlist(netlist)
      setValidationResult(result)
    } catch (error) {
      console.error('Validation error:', error)
    }
  }, [netlist, validateNetlist])

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-300 px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img
              src="/logo-full.svg"
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
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="horizontal">
          {/* Left Panel - JSON Editor and Validation */}
          <Panel defaultSize={50} minSize={30}>
            <PanelGroup direction="vertical">
              {/* JSON Editor */}
              <Panel defaultSize={60} minSize={30}>
                <div className="flex flex-col h-full">
                  <div className="bg-white border-b border-gray-200 px-4 py-2">
                    <div className="flex items-center justify-between">
                      <h2 className="text-sm font-medium text-gray-900">Netlist JSON</h2>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={handleManualValidation}
                          disabled={!netlist || isValidating}
                          className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                        >
                          {isValidating ? 'Validating...' : 'Validate'}
                        </button>
                        <select
                          onChange={(e) => {
                            const example = testExamples.find(ex => ex.id === e.target.value)
                            if (example) {
                              handleTestExampleSelect(example)
                            }
                          }}
                          className="text-xs border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          defaultValue=""
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
                          disabled={!netlist || isValidating}
                          className="p-1 rounded hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Validate netlist"
                        >
                          {isValidating ? (
                            <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <JsonEditor
                      value={netlist}
                      onChange={handleNetlistChange}
                      validationResult={validationResult}
                    />
                  </div>
                </div>
              </Panel>

              <PanelResizeHandle className="h-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

              {/* Validation Panel */}
              <Panel defaultSize={40} minSize={20}>
                <div className="flex flex-col h-full">
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
                  <div className="flex-1 overflow-auto">
                    <ValidationPanel validationResult={validationResult} />
                  </div>
                </div>
              </Panel>
            </PanelGroup>
          </Panel>

          <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors" />

          {/* Right Panel - Graph Visualization */}
          <Panel defaultSize={50} minSize={30}>
            <div className="flex flex-col h-full">
              <div className="bg-white border-b border-gray-200 px-4 py-2">
                <h2 className="text-sm font-medium text-gray-900">Schematic Visualization</h2>
              </div>
              <div className="flex-1">
                <GraphVisualization netlist={netlist} validationResult={validationResult} />
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  )
}

export default NetlistPage

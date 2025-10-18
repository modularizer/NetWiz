/**
 * JSON Editor Component
 *
 * A Monaco Editor-based JSON editor with:
 * - Syntax highlighting
 * - Real-time validation
 * - Error/warning markers
 * - Auto-formatting
 */

import React, { useRef, useEffect } from 'react'
import { Editor } from '@monaco-editor/react'
import type { Netlist, ValidationResult } from '@/types/netlist'

interface JsonEditorProps {
  value: Netlist | null
  onChange: (netlist: Netlist) => void
  validationResult?: ValidationResult | null
}

const JsonEditor: React.FC<JsonEditorProps> = ({ value, onChange, validationResult }) => {
  const editorRef = useRef<any>(null)

  // Convert netlist to JSON string
  const jsonString = value ? JSON.stringify(value, null, 2) : ''

  // Handle editor changes
  const handleEditorChange = (value: string | undefined) => {
    if (!value) return

    try {
      const parsed = JSON.parse(value)
      onChange(parsed)
    } catch (error) {
      // Invalid JSON - don't update the netlist
      console.warn('Invalid JSON:', error)
    }
  }

  // Set up error markers based on validation results
  useEffect(() => {
    if (!editorRef.current || !validationResult) return

    const editor = editorRef.current
    const model = editor.getModel()

    if (!model) return

    // Clear existing markers
    editor.deltaDecorations(editor.getModel()?.getAllDecorations() || [], [])

    // Add error markers
    const markers = validationResult.errors?.map((error) => ({
      startLineNumber: error.line_number || 1,
      startColumn: error.character_position || 1,
      endLineNumber: error.line_number || 1,
      endColumn: (error.character_position || 1) + 10,
      message: error.message,
      severity: 8, // Error severity
    })) || []

    // Add warning markers
    const warningMarkers = validationResult.warnings?.map((warning) => ({
      startLineNumber: warning.line_number || 1,
      startColumn: warning.character_position || 1,
      endLineNumber: warning.line_number || 1,
      endColumn: (warning.character_position || 1) + 10,
      message: warning.message,
      severity: 4, // Warning severity
    })) || []

    editor.deltaDecorations([], [...markers, ...warningMarkers])
  }, [validationResult])

  return (
    <div className="h-full">
      <Editor
        height="100%"
        defaultLanguage="json"
        value={jsonString}
        onChange={handleEditorChange}
        onMount={(editor) => {
          editorRef.current = editor
        }}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          formatOnPaste: true,
          formatOnType: true,
          tabSize: 2,
          insertSpaces: true,
          wordWrap: 'on',
          lineNumbers: 'on',
          folding: true,
          bracketPairColorization: { enabled: true },
        }}
        theme="vs-light"
      />
    </div>
  )
}

export default JsonEditor

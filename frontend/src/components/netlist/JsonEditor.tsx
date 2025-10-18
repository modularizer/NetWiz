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
import type { ValidationResult } from '@/types/netlist'

interface JsonEditorProps {
  value: string
  onChange: (jsonText: string) => void
  validationResult?: ValidationResult | null
  onNavigateToError?: (lineNumber: number, characterPosition: number) => void
}

const JsonEditor: React.FC<JsonEditorProps> = ({ value, onChange, validationResult, onNavigateToError }) => {
  const editorRef = useRef<any>(null)

  // Use the JSON text directly
  const jsonString = value || ''

  // Handle editor changes
  const handleEditorChange = (value: string | undefined) => {
    if (!value) return
    // Pass the raw JSON text directly
    onChange(value)
  }

  // Set up error markers based on validation results
  useEffect(() => {
    if (!editorRef.current || !validationResult) return

    const editor = editorRef.current
    const model = editor.getModel()

    if (!model) return

    // Clear existing markers
    editor.deltaDecorations(editor.getModel()?.getAllDecorations() || [], [])

    // Add error markers using Monaco's built-in decoration types
    const errorMarkers = validationResult.errors
      ?.filter(error => error.location && error.location.start_line_number > 0)
      ?.map((error) => {
        console.log('Creating marker for error:', error);
        return {
          range: {
            startLineNumber: error.location!.start_line_number,
            startColumn: error.location!.start_line_character_number,
            endLineNumber: error.location!.end_line_number,
            endColumn: error.location!.end_line_character_number,
          },
          options: {
            isWholeLine: false,
            className: 'error-squiggly',
            hoverMessage: {
              value: `❌ Error: ${error.message}`,
              isTrusted: true
            },
            glyphMarginClassName: 'error-glyph',
            minimap: {
              color: '#ff6b6b',
              position: 1
            },
            overviewRuler: {
              color: '#ff6b6b',
              position: 1
            }
          }
        };
      }) || [];

    // Add warning markers using Monaco's built-in decoration types
    const warningMarkers = validationResult.warnings
      ?.filter(warning => warning.location && warning.location.start_line_number > 0)
      ?.map((warning) => ({
        range: {
          startLineNumber: warning.location!.start_line_number,
          startColumn: warning.location!.start_line_character_number,
          endLineNumber: warning.location!.end_line_number,
          endColumn: warning.location!.end_line_character_number,
        },
        options: {
          isWholeLine: false,
          className: 'warning-squiggly',
          hoverMessage: {
            value: `⚠️ Warning: ${warning.message}`,
            isTrusted: true
          },
          glyphMarginClassName: 'warning-glyph',
          minimap: {
            color: '#ffa726',
            position: 2
          },
          overviewRuler: {
            color: '#ffa726',
            position: 2
          }
        },
      })) || [];

    console.log('Adding decorations:', errorMarkers.length, 'errors,', warningMarkers.length, 'warnings')
    console.log('Error data:', validationResult.errors)
    console.log('First error:', validationResult.errors?.[0])
    console.log('Error markers:', errorMarkers)
    console.log('First error marker:', errorMarkers[0])
    editor.deltaDecorations([], [...errorMarkers, ...warningMarkers])
  }, [validationResult])

  // Function to navigate to error location
  const navigateToError = (lineNumber: number, characterPosition: number) => {
    console.log('Navigating to:', lineNumber, characterPosition)
    if (!editorRef.current) return

    const editor = editorRef.current
    console.log('Editor found, setting position...')

    try {
      // Method 1: Focus first
      editor.focus()
      console.log('Editor focused')

      // Method 2: Set position
      const position = { lineNumber, column: characterPosition }
      editor.setPosition(position)
      console.log('Position set')

      // Method 3: Reveal range
      const range = {
        startLineNumber: lineNumber,
        startColumn: characterPosition,
        endLineNumber: lineNumber,
        endColumn: characterPosition + 1
      }
      editor.revealRange(range, 1) // 1 = center
      console.log('Range revealed')

      // Method 4: Set selection to highlight the error
      editor.setSelection(range)
      console.log('Selection set')

      // Method 5: Reveal line in center with delay
      setTimeout(() => {
        editor.revealLineInCenter(lineNumber)
        console.log('Line revealed in center (delayed)')
      }, 100)

    } catch (error) {
      console.error('Navigation error:', error)
    }
  }

  // Expose navigation function to parent component
  useEffect(() => {
    if (onNavigateToError) {
      // Store the navigation function for parent to use
      (window as any).navigateToJsonError = navigateToError
    }
  }, [onNavigateToError])

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <Editor
        height="100%"
        defaultLanguage="json"
        value={jsonString}
        onChange={handleEditorChange}
        onMount={(editor) => {
          editorRef.current = editor
          console.log('Monaco Editor mounted successfully')

          // Define custom decoration types
          editor.deltaDecorations([], [])

          // Test if Monaco Editor is working
          setTimeout(() => {
            if (editorRef.current) {
              console.log('Monaco Editor test: setting position to line 1, column 1')
              editorRef.current.setPosition({ lineNumber: 1, column: 1 })
            }
          }, 1000)
        }}
        options={{
          minimap: { enabled: true },
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
          glyphMargin: true,
          overviewRulerLanes: 3,
          scrollbar: {
            vertical: 'auto',
            horizontal: 'auto',
            verticalScrollbarSize: 12,
            horizontalScrollbarSize: 12,
          },
          smoothScrolling: true,
        }}
        theme="vs-light"
      />

      {/* Custom CSS for Monaco Editor decorations */}
      <style>{`
        .monaco-editor .error-squiggly {
          text-decoration: underline wavy #ff6b6b !important;
          text-decoration-thickness: 2px !important;
          text-underline-offset: 2px !important;
        }

        .monaco-editor .warning-squiggly {
          text-decoration: underline wavy #ffa726 !important;
          text-decoration-thickness: 2px !important;
          text-underline-offset: 2px !important;
        }

        .monaco-editor .error-glyph {
          background-color: #ff6b6b !important;
          color: white !important;
          border-radius: 50% !important;
          width: 16px !important;
          height: 16px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          font-size: 10px !important;
          font-weight: bold !important;
        }

        .monaco-editor .warning-glyph {
          background-color: #ffa726 !important;
          color: white !important;
          border-radius: 50% !important;
          width: 16px !important;
          height: 16px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          font-size: 10px !important;
          font-weight: bold !important;
        }

        /* Alternative approach using Monaco's decoration classes */
        .monaco-editor .view-overlays .error-squiggly {
          text-decoration: underline wavy #ff6b6b !important;
          text-decoration-thickness: 2px !important;
        }

        .monaco-editor .view-overlays .warning-squiggly {
          text-decoration: underline wavy #ffa726 !important;
          text-decoration-thickness: 2px !important;
        }
      `}</style>
    </div>
  )
}

export default JsonEditor

/**
 * Validation Panel Component
 *
 * Displays validation results including:
 * - Error and warning lists
 * - Location information
 * - Auto-fill suggestions
 * - Validation statistics
 */

import React from 'react'
import { AlertCircle, CheckCircle, AlertTriangle, Info, MapPin } from 'lucide-react'
import type { ValidationResult } from '@/types/netlist'

interface ValidationPanelProps {
  validationResult: ValidationResult | null
}

const ValidationPanel: React.FC<ValidationPanelProps> = ({ validationResult }) => {
  if (!validationResult) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-3 bg-gray-200 rounded-full flex items-center justify-center">
            <img
              src="/logo.svg"
              alt="NetWiz Logo"
              className="w-6 h-6"
            />
          </div>
          <p className="text-gray-500">No validation results</p>
          <p className="text-sm text-gray-400">Enter netlist data to see validation results</p>
        </div>
      </div>
    )
  }

  const { errors, warnings, auto_fill_suggestions, validation_rules_applied } = validationResult

  return (
    <div className="h-full bg-gray-50 p-4 space-y-4 overflow-auto">
      {/* Validation Summary */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center space-x-2 mb-2">
          {validationResult.is_valid ? (
            <CheckCircle className="w-5 h-5 text-success-500" />
          ) : (
            <AlertCircle className="w-5 h-5 text-error-500" />
          )}
          <h3 className="font-medium text-gray-900">
            {validationResult.is_valid ? 'Validation Passed' : 'Validation Failed'}
          </h3>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-error-600">{errors?.length || 0}</div>
            <div className="text-gray-500">Errors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">{warnings?.length || 0}</div>
            <div className="text-gray-500">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">{validation_rules_applied?.length || 0}</div>
            <div className="text-gray-500">Rules Applied</div>
          </div>
        </div>
      </div>

      {/* Errors */}
      {errors && errors.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-error-500" />
              <span>Errors ({errors.length})</span>
            </h4>
          </div>
          <div className="divide-y divide-gray-200">
            {errors.map((error, index) => (
              <div key={index} className="p-4">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="w-4 h-4 text-error-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{error.message}</p>
                    <div className="mt-1 flex items-center space-x-2 text-xs text-gray-500">
                      <span className="badge-error">{error.error_type}</span>
                      {error.line_number && (
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>Line {error.line_number}, Col {error.character_position}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-warning-500" />
              <span>Warnings ({warnings.length})</span>
            </h4>
          </div>
          <div className="divide-y divide-gray-200">
            {warnings.map((warning, index) => (
              <div key={index} className="p-4">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-4 h-4 text-warning-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{warning.message}</p>
                    <div className="mt-1 flex items-center space-x-2 text-xs text-gray-500">
                      <span className="badge-warning">{warning.error_type}</span>
                      {warning.line_number && (
                        <span className="flex items-center space-x-1">
                          <MapPin className="w-3 h-3" />
                          <span>Line {warning.line_number}, Col {warning.character_position}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Auto-fill Suggestions */}
      {auto_fill_suggestions && auto_fill_suggestions.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <Info className="w-4 h-4 text-primary-500" />
              <span>Auto-fill Suggestions ({auto_fill_suggestions.length})</span>
            </h4>
          </div>
          <div className="divide-y divide-gray-200">
            {auto_fill_suggestions.map((suggestion, index) => (
              <div key={index} className="p-4">
                <div className="flex items-start space-x-3">
                  <Info className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {suggestion.net_name} → {suggestion.suggested_type}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{suggestion.reason}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Applied Rules */}
      {validation_rules_applied && validation_rules_applied.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h4 className="font-medium text-gray-900">Applied Rules</h4>
          </div>
          <div className="p-4">
            <div className="flex flex-wrap gap-2">
              {validation_rules_applied.map((rule, index) => (
                <span key={index} className="badge-info text-xs">
                  {rule}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ValidationPanel

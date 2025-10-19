/**
 * Validation Panel Component
 *
 * Displays validation results including:
 * - Error and warning lists
 * - Location information
 * - Auto-fill suggestions
 * - Validation statistics
 */

import React, { useState } from 'react'
import { AlertCircle, CheckCircle, AlertTriangle, Info, MapPin, HelpCircle } from 'lucide-react'
import type { ValidationResult, ValidationErrorType } from '@/types/netlist'
import RulesModal from './RulesModal'
import RuleDescriptionModal from './RuleDescriptionModal'

interface ValidationPanelProps {
  validationResult: ValidationResult | null
  onNavigateToError?: (lineNumber: number, characterPosition: number) => void
}

const ValidationPanel: React.FC<ValidationPanelProps> = ({ validationResult, onNavigateToError }) => {
  const [isRulesModalOpen, setIsRulesModalOpen] = useState(false)
  const [isRuleDescriptionModalOpen, setIsRuleDescriptionModalOpen] = useState(false)
  const [selectedRule, setSelectedRule] = useState<ValidationErrorType | null>(null)

  const handleRuleDescriptionClick = (rule: ValidationErrorType) => {
    setSelectedRule(rule)
    setIsRuleDescriptionModalOpen(true)
  }

  if (!validationResult) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-3 bg-gray-200 rounded-full flex items-center justify-center">
            <img
              src={`${import.meta.env.VITE_BASE_URL}logo.svg`}
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
            <div
              className="text-2xl font-bold text-primary-600 cursor-pointer hover:text-primary-700 transition-colors"
              onClick={() => setIsRulesModalOpen(true)}
              title="Click to view rule descriptions"
            >
              {validation_rules_applied?.length || 0}
            </div>
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
            {errors.map((error, index) => {
              const hasLocation = error.location && error.location.start_line_number
              return (
                <div
                  key={index}
                  className={`p-4 ${hasLocation ? 'cursor-pointer hover:bg-gray-50 transition-colors' : ''}`}
                  onClick={() => {
                    console.log('ValidationPanel: Error clicked:', error.location)
                    if (hasLocation && onNavigateToError) {
                      console.log('ValidationPanel: Calling onNavigateToError')
                      onNavigateToError(error.location!.start_line_number, error.location!.start_line_character_number)
                    } else {
                      console.log('ValidationPanel: Cannot navigate - missing data or callback')
                    }
                  }}
                >
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-4 h-4 text-error-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{error.message}</p>
                      <div className="mt-1 flex items-center space-x-2 text-xs text-gray-500">
                        <span className="badge-error">{error.error_type.name}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRuleDescriptionClick(error.error_type)
                          }}
                          className="text-gray-400 hover:text-blue-600 transition-colors"
                          title="View rule description"
                        >
                          <HelpCircle className="w-3 h-3" />
                        </button>
                        {hasLocation && (
                          <span className={`flex items-center space-x-1 ${onNavigateToError ? 'text-blue-600 hover:text-blue-800' : ''}`}>
                            <MapPin className="w-3 h-3" />
                            <span>Line {error.location!.start_line_number}, Col {error.location!.start_line_character_number}</span>
                            {onNavigateToError && (
                              <span className="text-blue-500 ml-1">(click to navigate)</span>
                            )}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
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
            {warnings.map((warning, index) => {
              const hasLocation = warning.location && warning.location.start_line_number
              return (
                <div
                  key={index}
                  className={`p-4 ${hasLocation ? 'cursor-pointer hover:bg-gray-50 transition-colors' : ''}`}
                  onClick={() => {
                    if (hasLocation && onNavigateToError) {
                      onNavigateToError(warning.location!.start_line_number, warning.location!.start_line_character_number)
                    }
                  }}
                >
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="w-4 h-4 text-warning-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{warning.message}</p>
                      <div className="mt-1 flex items-center space-x-2 text-xs text-gray-500">
                        <span className="badge-warning">{warning.error_type.name}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRuleDescriptionClick(warning.error_type)
                          }}
                          className="text-gray-400 hover:text-blue-600 transition-colors"
                          title="View rule description"
                        >
                          <HelpCircle className="w-3 h-3" />
                        </button>
                        {hasLocation && (
                          <span className={`flex items-center space-x-1 ${onNavigateToError ? 'text-blue-600 hover:text-blue-800' : ''}`}>
                            <MapPin className="w-3 h-3" />
                            <span>Line {warning.location!.start_line_number}, Col {warning.location!.start_line_character_number}</span>
                            {onNavigateToError && (
                              <span className="text-blue-500 ml-1">(click to navigate)</span>
                            )}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
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
                <span
                  key={index}
                  className="badge-info text-xs cursor-pointer hover:bg-blue-600 transition-colors"
                  title={rule.description}
                >
                  {rule.name}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Rules Modal */}
      <RulesModal
        isOpen={isRulesModalOpen}
        onClose={() => setIsRulesModalOpen(false)}
        rules={validation_rules_applied || []}
      />

      {/* Rule Description Modal */}
      <RuleDescriptionModal
        isOpen={isRuleDescriptionModalOpen}
        onClose={() => setIsRuleDescriptionModalOpen(false)}
        rule={selectedRule}
      />
    </div>
  )
}

export default ValidationPanel

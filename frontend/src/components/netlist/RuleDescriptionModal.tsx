/**
 * RuleDescriptionModal Component
 *
 * A modal that displays detailed description of a specific validation rule.
 * Shows when user clicks on the question mark icon next to an error or warning.
 */

import React from 'react'
import { X, Info } from 'lucide-react'
import type { ValidationErrorType } from '@/types/netlist'

interface RuleDescriptionModalProps {
  isOpen: boolean
  onClose: () => void
  rule: ValidationErrorType | null
}

const RuleDescriptionModal: React.FC<RuleDescriptionModalProps> = ({ isOpen, onClose, rule }) => {
  if (!isOpen || !rule) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Info className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">
              Rule Description
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                {rule.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {rule.description}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RuleDescriptionModal

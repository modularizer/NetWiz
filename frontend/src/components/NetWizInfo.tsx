/**
 * NetWiz Info Component
 *
 * Displays information about what NetWiz is and what it does.
 * Used on authentication and backend check pages.
 */

export function NetWizInfo() {
  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-8 h-full flex flex-col justify-center">
      <div className="max-w-md mx-auto text-center">
        {/* Logo */}
        <div className="mb-6">
          <img
            src={'./logo-full.svg'}
            alt="NetWiz Logo"
            className="h-16 mx-auto mb-4"
          />
          <p className="text-lg text-gray-600">PCB Netlist Visualizer + Validator</p>
        </div>

        {/* Features */}
        <div className="space-y-4 mb-8">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Real-time Validation</h3>
              <p className="text-sm text-gray-600">Instantly validate your PCB netlists with comprehensive rule checking</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Interactive Visualization</h3>
              <p className="text-sm text-gray-600">Visualize your circuit connections with interactive graphs and schematics</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">File Upload Support</h3>
              <p className="text-sm text-gray-600">Upload JSON netlist files or paste directly into the editor</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Secure & Private</h3>
              <p className="text-sm text-gray-600">Your netlists are processed securely with user authentication</p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Ready to validate your PCB netlist?</strong>
          </p>
          <p className="text-xs text-gray-500">
            Sign in to access the full NetWiz experience with real-time validation and interactive visualization.
          </p>
        </div>
      </div>
    </div>
  )
}

/**
 * Base Path Context
 *
 * Provides a global context for the base path that is detected once
 * when the app loads from the root index.html
 */

import React, { createContext, useContext, useEffect, useState } from 'react'

interface BasePathContextType {
  basePath: string
  withBasePath: (path: string) => string
}

const BasePathContext = createContext<BasePathContextType | undefined>(undefined)

export const useBasePath = () => {
  const context = useContext(BasePathContext)
  if (context === undefined) {
    throw new Error('useBasePath must be used within a BasePathProvider')
  }
  return context
}

interface BasePathProviderProps {
  children: React.ReactNode
}

export const BasePathProvider: React.FC<BasePathProviderProps> = ({ children }) => {
  const [basePath, setBasePath] = useState<string>('/')

  useEffect(() => {
    // Detect base path once when the app loads from index.html
    const detectBasePath = () => {
      if (typeof window === 'undefined') {
        return '/'
      }

      // Use the base path detected by the HTML script if available
      if (window.__NETWIZ_BASE_PATH__) {
        console.log('BasePathContext: Using pre-detected base path:', window.__NETWIZ_BASE_PATH__)
        return window.__NETWIZ_BASE_PATH__
      }

      // Fallback: detect from current URL
      const pathname = window.location.pathname
      console.log('BasePathContext: window.location.href =', window.location.href)
      console.log('BasePathContext: pathname =', pathname)

      if (pathname === '/') {
        console.log('BasePathContext: At root, returning /')
        return '/'
      }

      const segments = pathname.split('/').filter(Boolean)
      console.log('BasePathContext: segments =', segments)

      if (segments.length === 0) {
        console.log('BasePathContext: No segments, returning /')
        return '/'
      }

      const result = `/${segments[0]}/`
      console.log('BasePathContext: Returning base path =', result)
      return result
    }

    const detectedBasePath = detectBasePath()
    console.log('BasePathContext: Final detected base path =', detectedBasePath)
    setBasePath(detectedBasePath)
  }, [])

  const withBasePath = (path: string): string => {
    // Remove leading slash from path to avoid double slashes
    const cleanPath = path.startsWith('/') ? path.slice(1) : path
    const result = `${basePath}${cleanPath}`
    console.log(`BasePathContext: withBasePath("${path}") -> "${result}" (basePath="${basePath}")`)
    return result
  }

  const value: BasePathContextType = {
    basePath,
    withBasePath,
  }

  return (
    <BasePathContext.Provider value={value}>
      {children}
    </BasePathContext.Provider>
  )
}

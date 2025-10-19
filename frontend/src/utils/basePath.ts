/**
 * Base Path Detection Utility
 *
 * Detects the actual base path from window.location and provides utilities
 * for constructing URLs that work in both development and production.
 */

// Detect the base path from the current URL
export function detectBasePath(): string {
  if (typeof window === 'undefined') {
    // Server-side rendering fallback
    return '/'
  }

  // If we're at the homepage root, return the base path from location.href
  if (window.location.pathname === '/' || window.location.pathname === '/NetWiz/') {
    const url = new URL(window.location.href)
    return url.pathname === '/' ? '/' : '/NetWiz/'
  }

  // Otherwise, extract the base path from the URL
  const url = new URL(window.location.href)
  const pathname = url.pathname

  // Extract the base path - everything up to the last segment
  const segments = pathname.split('/').filter(Boolean)
  if (segments.length === 0) {
    return '/'
  }

  // Return the base path with trailing slash
  return `/${segments[0]}/`
}

// Get the base path (cached)
let cachedBasePath: string | null = null
export function getBasePath(): string {
  if (cachedBasePath === null) {
    cachedBasePath = detectBasePath()
  }
  return cachedBasePath
}

// Construct a URL with the proper base path
export function withBasePath(path: string): string {
  const basePath = getBasePath()

  // Remove leading slash from path to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path

  return `${basePath}${cleanPath}`
}

// Save the base path to localStorage for persistence
export function saveBasePath(): void {
  if (typeof window !== 'undefined') {
    const basePath = detectBasePath()
    localStorage.setItem('netwiz-base-path', basePath)
  }
}

// Load the base path from localStorage (fallback)
export function loadBasePath(): string {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('netwiz-base-path')
    if (saved) {
      return saved
    }
  }
  return detectBasePath()
}

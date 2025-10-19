/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_BASE_URL: string
  readonly VITE_BACKEND_PORT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Global variable set by index.html
declare global {
  interface Window {
    __NETWIZ_BASE_PATH__?: string
  }
}

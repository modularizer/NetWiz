/// <reference types="vite/client" />



// Global variable set by index.html
declare global {
  interface Window {
    __NETWIZ_BASE_PATH__?: string
  }
}

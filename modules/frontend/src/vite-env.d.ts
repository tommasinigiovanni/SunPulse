/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_AUTH0_DOMAIN: string
  readonly VITE_AUTH0_CLIENT_ID: string
  readonly VITE_AUTH0_AUDIENCE: string
  readonly VITE_APP_NAME: string
  readonly VITE_ENVIRONMENT: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly VITE_ENABLE_REALTIME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 
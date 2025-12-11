import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import App from './App';

// Configurazione React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 secondi
      cacheTime: 5 * 60 * 1000, // 5 minuti
      retry: (failureCount, error: any) => {
        // Non ritentare per errori 4xx
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Error boundary per gestire errori React
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React Error Boundary:', error, errorInfo);
    
    // Qui potresti inviare l'errore a un servizio di monitoring
    // come Sentry, LogRocket, etc.
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          padding: 24,
          textAlign: 'center'
        }}>
          <h1 style={{ color: '#ff4d4f', marginBottom: 16 }}>
            Oops! Qualcosa è andato storto
          </h1>
          <p style={{ color: '#666', marginBottom: 24 }}>
            Si è verificato un errore imprevisto nell'applicazione.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              backgroundColor: '#1890ff',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer'
            }}
          >
            Ricarica la pagina
          </button>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: 24, textAlign: 'left' }}>
              <summary style={{ cursor: 'pointer', marginBottom: 8 }}>
                Dettagli errore (development)
              </summary>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: 16, 
                borderRadius: 4,
                fontSize: 12,
                overflow: 'auto',
                maxWidth: '80vw'
              }}>
                {this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Render dell'applicazione
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
        {/* {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )} */}
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// Service Worker disabled for now
// TODO: Add service worker in production
// if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
//   window.addEventListener('load', () => {
//     navigator.serviceWorker.register('/sw.js')
//       .then((registration) => {
//         console.log('SW registered: ', registration);
//       })
//       .catch((registrationError) => {
//         console.log('SW registration failed: ', registrationError);
//       });
//   });
// } 
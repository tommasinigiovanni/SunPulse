import React, { createContext, useContext } from 'react';
import { Auth0Provider, useAuth0 as useAuth0Real } from '@auth0/auth0-react';

interface AuthProviderProps {
  children: React.ReactNode;
}

// Interfaccia compatibile con Auth0
interface MockAuth0Context {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: any;
  error?: Error;
  loginWithRedirect: () => Promise<void>;
  logout: () => void;
  getAccessTokenSilently: () => Promise<string>;
}

// Context per il mock
const MockAuth0Context = createContext<MockAuth0Context | undefined>(undefined);

// Mock Auth per sviluppo quando Auth0 non è configurato
const MockAuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const mockAuth: MockAuth0Context = {
    isLoading: false,
    isAuthenticated: true,
    user: {
      sub: 'mock-user-dev',
      name: 'Sviluppatore',
      email: 'dev@solardashboard.com',
      picture: '👨‍💻'
    },
    error: undefined,
    loginWithRedirect: async () => console.log('Mock login'),
    logout: () => window.location.reload(),
    getAccessTokenSilently: async () => 'mock-dev-token'
  };

  return (
    <MockAuth0Context.Provider value={mockAuth}>
      <div>
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          background: '#ff6b35',
          color: 'white',
          padding: '5px 10px',
          fontSize: '12px',
          textAlign: 'center',
          zIndex: 9999
        }}>
          🔧 MODALITÀ SVILUPPO - Auth0 disabilitato
        </div>
        <div style={{ paddingTop: '30px' }}>
          {children}
        </div>
      </div>
    </MockAuth0Context.Provider>
  );
};

// Hook che gestisce sia mock che real Auth0
const useMockAuth0 = () => {
  const context = useContext(MockAuth0Context);
  if (context === undefined) {
    throw new Error('useMockAuth0 must be used within a MockAuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;
  const redirectUri = window.location.origin;

  // Modalità sviluppo se Auth0 non configurato o è il dominio di test
  const isDevelopmentMode = true; // FORZATO PER TEST

  if (isDevelopmentMode) {
    console.warn('🔧 Auth0 non configurato correttamente - usando modalità sviluppo');
    return <MockAuthProvider>{children}</MockAuthProvider>;
  }

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience: audience,
        scope: "openid profile email"
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      {children}
    </Auth0Provider>
  );
};

// Export hook che funziona con entrambi i provider
export const useAuth0 = () => {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const isDevelopmentMode = !domain || domain.includes('gt0dev.eu.auth0.com');
  
  if (isDevelopmentMode) {
    return useMockAuth0();
  } else {
    return useAuth0Real();
  }
}; 
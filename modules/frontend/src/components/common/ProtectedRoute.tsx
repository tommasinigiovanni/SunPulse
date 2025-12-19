import React from 'react';
import { useAuth0 } from '../../providers/AuthProvider';
import { Spin, Result, Button } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { LandingPage } from '../../pages/LandingPage';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = [],
  fallback
}) => {
  const { isAuthenticated, isLoading, loginWithRedirect, user, error } = useAuth0();

  // Loading state con logo
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: 24,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}>
        <img 
          src="/sunpulse-logo.png" 
          alt="SunPulse" 
          style={{ 
            width: 80, 
            height: 80, 
            borderRadius: '50%',
            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            animation: 'pulse 2s ease-in-out infinite',
          }} 
        />
        <Spin 
          size="large" 
          indicator={<LoadingOutlined style={{ fontSize: 32, color: '#fff' }} spin />}
        />
        <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: 16 }}>
          Caricamento SunPulse...
        </div>
        <style>{`
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
          }
        `}</style>
      </div>
    );
  }

  // Authentication error
  if (error) {
    return (
      <Result
        status="error"
        title="Errore di Autenticazione"
        subTitle={error.message || 'Si è verificato un errore durante l\'autenticazione'}
        extra={
          <Button type="primary" onClick={() => loginWithRedirect()}>
            Riprova Login
          </Button>
        }
      />
    );
  }

  // Not authenticated - mostra landing page
  if (!isAuthenticated) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return <LandingPage onLogin={() => loginWithRedirect()} />;
  }

  // Check permissions if required
  if (requiredPermissions.length > 0) {
    const userPermissions = user?.['https://sunpulse/permissions'] || [];
    const userRoles = user?.['https://sunpulse/roles'] || [];
    
    const hasRequiredPermission = requiredPermissions.some(permission => 
      userPermissions.includes(permission) || 
      userRoles.includes('admin') || 
      userRoles.includes('operator')
    );

    if (!hasRequiredPermission) {
      return (
        <Result
          status="403"
          title="Accesso Negato"
          subTitle="Non hai i permessi necessari per accedere a questa pagina"
          extra={
            <Button type="primary" onClick={() => window.history.back()}>
              Torna Indietro
            </Button>
          }
        />
      );
    }
  }

  // Authorized - render children
  return <>{children}</>;
}; 
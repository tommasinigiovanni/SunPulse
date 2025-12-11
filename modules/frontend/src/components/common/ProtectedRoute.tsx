import React from 'react';
import { useAuth0 } from '../../providers/AuthProvider';
import { Spin, Result, Button } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

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

  // Loading state
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: 16
      }}>
        <Spin 
          size="large" 
          indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
        />
        <div style={{ color: '#666', fontSize: 16 }}>
          Caricamento autenticazione...
        </div>
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

  // Not authenticated
  if (!isAuthenticated) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <Result
        status="403"
        title="Accesso Richiesto"
        subTitle="Devi effettuare il login per accedere a questa pagina"
        extra={
          <Button type="primary" onClick={() => loginWithRedirect()}>
            Accedi
          </Button>
        }
      />
    );
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
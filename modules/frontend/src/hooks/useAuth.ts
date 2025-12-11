import { useAuth0 } from '../providers/AuthProvider';
import { useMemo } from 'react';

export const useAuth = () => {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    getAccessTokenSilently, 
    loginWithRedirect, 
    logout 
  } = useAuth0();

  const getAuthHeaders = async (): Promise<Record<string, string>> => {
    if (!isAuthenticated) {
      console.warn('Utente non autenticato');
      return {};
    }
    
    try {
      const token = await getAccessTokenSilently();
      
      return {
        Authorization: `Bearer ${token}`,
      };
    } catch (error) {
      console.error('Errore nel recupero del token:', error);
      // Prova a fare login di nuovo se il token non è valido
      await loginWithRedirect();
      return {};
    }
  };

  const login = () => {
    loginWithRedirect();
  };

  const logoutUser = () => {
    logout();
  };

  // Informazioni utente formattate
  const userInfo = useMemo(() => {
    if (!user) return null;
    
    return {
      id: user.sub || '',
      name: user.name || user.nickname || 'Utente',
      email: user.email || '',
      picture: user.picture || '',
      roles: user['https://sunpulse/roles'] || [],
      permissions: user['https://sunpulse/permissions'] || [],
    };
  }, [user]);

  // Check permessi
  const hasPermission = (permission: string): boolean => {
    if (!userInfo?.permissions) return false;
    return userInfo.permissions.includes(permission);
  };

  const hasRole = (role: string): boolean => {
    if (!userInfo?.roles) return false;
    return userInfo.roles.includes(role);
  };

  // Permessi specifici per l'app
  const canViewDevices = hasPermission('read:devices') || hasRole('admin');
  const canManageDevices = hasPermission('write:devices') || hasRole('admin');
  const canViewAnalytics = hasPermission('read:analytics') || hasRole('admin');

  return {
    // Stato autenticazione
    user: userInfo,
    isAuthenticated,
    isLoading,
    
    // Metodi autenticazione
    login,
    logout: logoutUser,
    getAuthHeaders,
    
    // Controllo permessi
    hasPermission,
    hasRole,
    canViewDevices,
    canManageDevices,
    canViewAnalytics,
  };
}; 
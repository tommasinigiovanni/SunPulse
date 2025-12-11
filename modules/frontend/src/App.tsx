import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { Refine } from "@refinedev/core";
import { DevtoolsProvider } from "@refinedev/devtools";
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";
import { ThemedLayoutV2, RefineThemes } from "@refinedev/antd";
import { ConfigProvider, Layout, notification } from "antd";
import { 
  DashboardOutlined, 
  ControlOutlined, 
  BarChartOutlined,
  SettingOutlined,
  BellOutlined
} from '@ant-design/icons';
import routerBindings from "@refinedev/react-router-v6";

// Providers
import { AuthProvider } from './providers/AuthProvider';
import { dataProvider } from './providers/DataProvider';

// Components
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Header } from './components/layout/Header';

// Pages
import { Dashboard } from './pages/Dashboard';
import { DeviceList } from './components/devices/DeviceList';

// Utils
import { setAuthTokenGetter } from './utils/api';
import { useAuth } from './hooks/useAuth';
import { NOTIFICATION_CONFIG } from './utils/constants';

// Styles
import '@refinedev/antd/dist/reset.css';
import './styles/global.css';

// Configurazione notifiche globali
notification.config({
  duration: NOTIFICATION_CONFIG.DURATION,
  placement: NOTIFICATION_CONFIG.PLACEMENT,
  maxCount: NOTIFICATION_CONFIG.MAX_COUNT,
});

// Layout interno per pagine autenticate
const AuthenticatedLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <ThemedLayoutV2
      Header={() => <Header collapsed={collapsed} onCollapse={setCollapsed} />}
      Title={({ collapsed }) => (
        <div style={{ 
          fontSize: collapsed ? 14 : 16, 
          fontWeight: 'bold',
          color: '#1890ff'
        }}>
          {collapsed ? 'SD' : 'SunPulse'}
        </div>
      )}
    >
      <Outlet />
    </ThemedLayoutV2>
  );
};

// Componente per setup Auth token
const AuthTokenSetup: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    // Configura il getter del token per axios
    setAuthTokenGetter(async () => {
      const headers = await getAuthHeaders();
      return headers.Authorization?.replace('Bearer ', '') || null;
    });
  }, [getAuthHeaders]);

  return <>{children}</>;
};

// App principale
function App() {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <BrowserRouter>
      <RefineKbarProvider>
        <ConfigProvider theme={RefineThemes.Blue}>
          <AuthProvider>
            <AuthTokenSetup>
              {isDevelopment ? (
                <DevtoolsProvider>
                  <AppContent />
                </DevtoolsProvider>
              ) : (
                <AppContent />
              )}
            </AuthTokenSetup>
          </AuthProvider>
        </ConfigProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

// Contenuto principale dell'app
const AppContent: React.FC = () => {
  return (
    <Refine
      dataProvider={dataProvider}
      routerProvider={routerBindings}
      resources={[
        {
          name: "dashboard",
          list: "/",
          meta: { 
            icon: <DashboardOutlined />,
            label: "Dashboard"
          }
        },
        {
          name: "devices",
          list: "/devices",
          show: "/devices/:id",
          meta: { 
            icon: <ControlOutlined />,
            label: "Dispositivi"
          }
        },
        {
          name: "analytics",
          list: "/analytics", 
          meta: { 
            icon: <BarChartOutlined />,
            label: "Analytics"
          }
        },
        {
          name: "alarms",
          list: "/alarms",
          meta: { 
            icon: <BellOutlined />,
            label: "Allarmi"
          }
        },
        {
          name: "settings",
          list: "/settings",
          meta: { 
            icon: <SettingOutlined />,
            label: "Impostazioni"
          }
        }
      ]}
      options={{
        syncWithLocation: true,
        warnWhenUnsavedChanges: true,
        projectId: "sunpulse",
      }}
    >
      <Routes>
        <Route
          element={
            <ProtectedRoute>
              <AuthenticatedLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard principale */}
          <Route index element={<Dashboard />} />
          
          {/* Gestione dispositivi */}
          <Route 
            path="/devices" 
            element={
              <div style={{ padding: 24 }}>
                <DeviceList onDeviceClick={(device) => {
                  // Navigate to device detail
                  window.location.href = `/devices/${device.id}`;
                }} />
              </div>
            } 
          />
          
          {/* Pagina dispositivo singolo */}
          <Route 
            path="/devices/:id" 
            element={
              <div style={{ padding: 24 }}>
                <div>Device Detail Page - TODO</div>
              </div>
            } 
          />
          
          {/* Analytics */}
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute requiredPermissions={['read:analytics']}>
                <div style={{ padding: 24 }}>
                  <div>Analytics Page - TODO</div>
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* Allarmi */}
          <Route 
            path="/alarms" 
            element={
              <div style={{ padding: 24 }}>
                <div>Alarms Page - TODO</div>
              </div>
            } 
          />
          
          {/* Impostazioni */}
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute requiredPermissions={['admin']}>
                <div style={{ padding: 24 }}>
                  <div>Settings Page - TODO</div>
                </div>
              </ProtectedRoute>
            } 
          />
        </Route>
        
        {/* Route per errori */}
        <Route 
          path="*" 
          element={
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100vh' 
            }}>
              <div>Pagina non trovata</div>
            </div>
          } 
        />
      </Routes>
      
      <RefineKbar />
    </Refine>
  );
};

export default App; 
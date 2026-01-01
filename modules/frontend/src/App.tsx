import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Outlet, useNavigate } from 'react-router-dom';
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
import ErrorBoundary from './components/common/ErrorBoundary';

// Pages
import { Dashboard } from './pages/Dashboard';
import { DeviceDetail } from './pages/DeviceDetail';
import { Analytics } from './pages/Analytics';
import { Alarms } from './pages/Alarms';
import { Settings } from './pages/Settings';
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

// Componente Logo per Sidebar
const SidebarTitle: React.FC<{ collapsed: boolean }> = ({ collapsed }) => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center', 
    gap: 8,
    padding: collapsed ? '8px 0' : '8px 4px',
    justifyContent: collapsed ? 'center' : 'flex-start',
  }}>
    <img 
      src="/sunpulse-logo.png" 
      alt="SunPulse" 
      style={{ 
        width: collapsed ? 32 : 36, 
        height: collapsed ? 32 : 36,
        borderRadius: '50%',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      }} 
    />
    {!collapsed && (
      <span style={{ 
        fontSize: 18, 
        fontWeight: 700,
        background: 'linear-gradient(90deg, #f5a623, #1890ff)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}>
        SunPulse
      </span>
    )}
  </div>
);

// Footer con credits
const AppFooter: React.FC = () => (
  <div style={{
    textAlign: 'center',
    padding: '12px 24px',
    background: '#fafafa',
    borderTop: '1px solid #f0f0f0',
    fontSize: 12,
    color: '#8c8c8c',
  }}>
    <span>Made with ☀️ by </span>
    <a 
      href="https://giovannitommasini.it" 
      target="_blank" 
      rel="noopener noreferrer"
      style={{ color: '#1890ff', fontWeight: 500 }}
    >
      Giovanni Tommasini
    </a>
    <span style={{ margin: '0 8px' }}>•</span>
    <span>© {new Date().getFullYear()} SunPulse</span>
  </div>
);

// Layout interno per pagine autenticate
const AuthenticatedLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <ThemedLayoutV2
      Header={() => <Header collapsed={collapsed} onCollapse={setCollapsed} />}
      Title={({ collapsed }) => <SidebarTitle collapsed={collapsed} />}
      Footer={() => <AppFooter />}
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
    <ErrorBoundary showDetails={isDevelopment}>
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
    </ErrorBoundary>
  );
}

// Pagina lista dispositivi con navigazione
const DevicesPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: 24 }}>
      <DeviceList onDeviceClick={(device) => {
        // Usa thing_key come ID per la navigazione (è l'identificatore ZCS)
        const deviceId = (device as any).thing_key || device.id;
        navigate(`/devices/${deviceId}`);
      }} />
    </div>
  );
};

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
            element={<DevicesPage />} 
          />
          
          {/* Pagina dispositivo singolo */}
          <Route 
            path="/devices/:id" 
            element={<DeviceDetail />} 
          />
          
          {/* Analytics */}
          <Route 
            path="/analytics" 
            element={<Analytics />} 
          />
          
          {/* Allarmi */}
          <Route 
            path="/alarms" 
            element={<Alarms />} 
          />
          
          {/* Impostazioni */}
          <Route 
            path="/settings" 
            element={<Settings />} 
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
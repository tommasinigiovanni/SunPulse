import React from 'react';
import { Layout, Avatar, Dropdown, Space, Typography, Button } from 'antd';
import { 
  UserOutlined, 
  LogoutOutlined, 
  SettingOutlined, 
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  WifiOutlined
} from '@ant-design/icons';
import { useAuth } from '@/hooks/useAuth';
import { useRealTimeData } from '@/hooks/useRealTimeData';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

interface HeaderProps {
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({ collapsed, onCollapse }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const { isWebSocketConnected, summary } = useRealTimeData();
  
  // WebSocket è disabilitato se VITE_ENABLE_REALTIME è false
  const isRealtimeEnabled = import.meta.env.VITE_ENABLE_REALTIME === 'true';

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profilo',
      onClick: () => {
        // Navigate to profile page
        console.log('Navigate to profile');
      },
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Impostazioni',
      onClick: () => {
        // Navigate to settings page
        console.log('Navigate to settings');
      },
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Esci',
      onClick: () => logout(),
    },
  ];

  return (
    <AntHeader
      style={{
        padding: '0 16px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 1px 4px rgba(0,21,41,.08)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Collapse Button */}
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => onCollapse?.(!collapsed)}
          style={{
            fontSize: '16px',
            width: 32,
            height: 32,
          }}
        />

        {/* App Title with Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <img 
            src="/sunpulse-logo.png" 
            alt="SunPulse" 
            style={{ 
              width: 28, 
              height: 28, 
              borderRadius: '50%',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            }} 
          />
          <Text 
            strong 
            style={{ 
              fontSize: 18, 
              background: 'linear-gradient(90deg, #f5a623, #1890ff)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            SunPulse
          </Text>
          
          {/* Connection Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <WifiOutlined 
              style={{ 
                color: isRealtimeEnabled 
                  ? (isWebSocketConnected ? '#52c41a' : '#ff4d4f')
                  : '#1890ff',
                fontSize: 14 
              }} 
            />
            <Text 
              type={isRealtimeEnabled 
                ? (isWebSocketConnected ? 'success' : 'danger')
                : undefined
              } 
              style={{ fontSize: 12, color: isRealtimeEnabled ? undefined : '#1890ff' }}
            >
              {isRealtimeEnabled 
                ? (isWebSocketConnected ? 'Connesso' : 'Disconnesso')
                : 'Polling'
              }
            </Text>
          </div>
        </div>
      </div>

      {/* Right Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Quick Stats */}
        {summary && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 24,
            marginRight: 16,
            padding: '4px 0'
          }}>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              minWidth: 70
            }}>
              <Text type="secondary" style={{ fontSize: 11, lineHeight: 1.2 }}>Produzione</Text>
              <Text strong style={{ color: '#1890ff', fontSize: 14, lineHeight: 1.4 }}>
                {((summary.total_power || 0) / 1000).toFixed(1)} kW
              </Text>
            </div>
            
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              minWidth: 70
            }}>
              <Text type="secondary" style={{ fontSize: 11, lineHeight: 1.2 }}>Energia Oggi</Text>
              <Text strong style={{ color: '#52c41a', fontSize: 14, lineHeight: 1.4 }}>
                {(summary.total_energy_today || 0).toFixed(1)} kWh
              </Text>
            </div>
            
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              minWidth: 70
            }}>
              <Text type="secondary" style={{ fontSize: 11, lineHeight: 1.2 }}>Dispositivi</Text>
              <Text strong style={{ fontSize: 14, lineHeight: 1.4 }}>
                <span style={{ color: '#52c41a' }}>{summary.online_devices ?? summary.active_devices ?? 0}</span>
                <span style={{ color: '#999' }}>/</span>
                <span style={{ color: '#666' }}>{summary.total_devices ?? summary.active_devices ?? 0}</span>
              </Text>
            </div>
          </div>
        )}

        {/* Notifications - TODO: implementare sistema notifiche */}
        <Button
          type="text"
          icon={<BellOutlined />}
          style={{
            fontSize: '16px',
            width: 32,
            height: 32,
          }}
        />

        {/* User Menu */}
        {isAuthenticated && user && (
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            arrow
          >
            <div 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 8, 
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 6,
                transition: 'background-color 0.2s',
                maxWidth: 200,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <Avatar 
                size="small" 
                src={user.picture}
                icon={<UserOutlined />}
              />
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                overflow: 'hidden',
                minWidth: 0,
              }}>
                <Text 
                  strong 
                  ellipsis 
                  style={{ fontSize: 13, lineHeight: 1.3 }}
                >
                  {user.name}
                </Text>
                <Text 
                  type="secondary" 
                  ellipsis
                  style={{ fontSize: 11, lineHeight: 1.3 }}
                >
                  {user.email}
                </Text>
              </div>
            </div>
          </Dropdown>
        )}
      </div>
    </AntHeader>
  );
}; 
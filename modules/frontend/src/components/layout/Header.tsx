import React from 'react';
import { Layout, Avatar, Dropdown, Space, Typography, Button, Badge } from 'antd';
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

  const notificationCount = 3; // TODO: Get from real notification system

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

        {/* App Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text strong style={{ fontSize: 18, color: '#1890ff' }}>
            SunPulse
          </Text>
          
          {/* Connection Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <WifiOutlined 
              style={{ 
                color: isWebSocketConnected ? '#52c41a' : '#ff4d4f',
                fontSize: 14 
              }} 
            />
            <Text 
              type={isWebSocketConnected ? 'success' : 'danger'} 
              style={{ fontSize: 12 }}
            >
              {isWebSocketConnected ? 'Connesso' : 'Disconnesso'}
            </Text>
          </div>
        </div>
      </div>

      {/* Right Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Quick Stats */}
        {summary && (
          <Space size="large">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 12, color: '#666' }}>Produzione</div>
              <Text strong style={{ color: '#1890ff' }}>
                {(summary.total_power / 1000).toFixed(1)} kW
              </Text>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 12, color: '#666' }}>Energia Oggi</div>
              <Text strong style={{ color: '#52c41a' }}>
                {summary.total_energy_today.toFixed(1)} kWh
              </Text>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 12, color: '#666' }}>Dispositivi</div>
              <Text strong>
                <span style={{ color: '#52c41a' }}>{summary.online_devices}</span>
                /
                <span style={{ color: '#666' }}>{summary.total_devices}</span>
              </Text>
            </div>
          </Space>
        )}

        {/* Notifications */}
        <Badge count={notificationCount} size="small">
          <Button
            type="text"
            icon={<BellOutlined />}
            onClick={() => {
              // Open notifications panel
              console.log('Open notifications');
            }}
            style={{
              fontSize: '16px',
              width: 32,
              height: 32,
            }}
          />
        </Badge>

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
              <Space direction="vertical" size={0}>
                <Text strong style={{ fontSize: 14, lineHeight: 1.2 }}>
                  {user.name}
                </Text>
                <Text type="secondary" style={{ fontSize: 12, lineHeight: 1.2 }}>
                  {user.email}
                </Text>
              </Space>
            </div>
          </Dropdown>
        )}
      </div>
    </AntHeader>
  );
}; 
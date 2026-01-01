import React, { useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Form, 
  Input, 
  Button, 
  Switch, 
  Select,
  Typography, 
  Space, 
  Divider,
  InputNumber,
  Tabs,
  Descriptions,
  Tag,
  Spin,
  Alert,
  Skeleton
} from 'antd';
import { 
  SettingOutlined,
  BellOutlined,
  ThunderboltOutlined,
  SaveOutlined,
  ApiOutlined,
  DatabaseOutlined,
  SecurityScanOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined
} from '@ant-design/icons';

import { useSettings, useSettingsDevices, useApiStatus } from '../hooks/useSettings';
import { UserSettingsUpdate } from '../utils/api';

const { Title, Text } = Typography;
const { Option } = Select;

export const Settings: React.FC = () => {
  const [form] = Form.useForm();
  
  // Hooks for data
  const { settings, isLoading, isError, updateSettings, isUpdating } = useSettings();
  const { devices, isLoading: devicesLoading, refetch: refetchDevices } = useSettingsDevices();
  const { status: apiStatus, isLoading: apiLoading, refetch: refetchApiStatus } = useApiStatus();

  // Populate form when settings load
  useEffect(() => {
    if (settings) {
      form.setFieldsValue({
        system_name: settings.system_name,
        language: settings.language,
        timezone: settings.timezone,
        currency: settings.currency,
        energy_price: settings.energy_price,
        sell_price: settings.sell_price,
        notification_email: settings.notification_email,
        notify_critical_alarms: settings.notify_critical_alarms,
        notify_warnings: settings.notify_warnings,
        notify_daily_report: settings.notify_daily_report,
        notify_weekly_report: settings.notify_weekly_report,
        battery_low_threshold: settings.battery_low_threshold,
        battery_critical_threshold: settings.battery_critical_threshold,
        realtime_interval: settings.realtime_interval,
        historical_interval: settings.historical_interval,
      });
    }
  }, [settings, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const updateData: UserSettingsUpdate = {
        system_name: values.system_name,
        language: values.language,
        timezone: values.timezone,
        currency: values.currency,
        energy_price: values.energy_price,
        sell_price: values.sell_price,
        notification_email: values.notification_email || null,
        notify_critical_alarms: values.notify_critical_alarms,
        notify_warnings: values.notify_warnings,
        notify_daily_report: values.notify_daily_report,
        notify_weekly_report: values.notify_weekly_report,
        battery_low_threshold: values.battery_low_threshold,
        battery_critical_threshold: values.battery_critical_threshold,
        realtime_interval: values.realtime_interval,
        historical_interval: values.historical_interval,
      };
      await updateSettings(updateData);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'green';
      case 'offline': return 'red';
      default: return 'orange';
    }
  };

  const tabItems = [
    {
      key: 'general',
      label: (
        <span>
          <SettingOutlined />
          Generale
        </span>
      ),
      children: isLoading ? (
        <Skeleton active paragraph={{ rows: 6 }} />
      ) : (
        <Form form={form} layout="vertical">
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item label="Nome Impianto" name="system_name">
                <Input placeholder="Es: Casa Tommasini" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Lingua" name="language">
                <Select>
                  <Option value="it">Italiano</Option>
                  <Option value="en">English</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Fuso Orario" name="timezone">
                <Select>
                  <Option value="Europe/Rome">Europe/Rome (UTC+1)</Option>
                  <Option value="Europe/London">Europe/London (UTC+0)</Option>
                  <Option value="America/New_York">America/New_York (UTC-5)</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Valuta" name="currency">
                <Select>
                  <Option value="EUR">Euro (€)</Option>
                  <Option value="USD">US Dollar ($)</Option>
                  <Option value="GBP">British Pound (£)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>Tariffe Energia</Divider>

          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item 
                label="Prezzo Acquisto Energia (€/kWh)" 
                name="energy_price"
                help="Costo dell'energia acquistata dalla rete"
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.01}
                  precision={2}
                  style={{ width: '100%' }}
                  addonAfter="€/kWh"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item 
                label="Prezzo Vendita Energia (€/kWh)" 
                name="sell_price"
                help="Ricavo dalla vendita di energia alla rete"
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.01}
                  precision={2}
                  style={{ width: '100%' }}
                  addonAfter="€/kWh"
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      ),
    },
    {
      key: 'notifications',
      label: (
        <span>
          <BellOutlined />
          Notifiche
        </span>
      ),
      children: isLoading ? (
        <Skeleton active paragraph={{ rows: 6 }} />
      ) : (
        <Form form={form} layout="vertical">
          <Card title="Notifiche Email" size="small" style={{ marginBottom: 16 }}>
            <Form.Item label="Email" name="notification_email">
              <Input placeholder="email@esempio.com" type="email" />
            </Form.Item>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Allarmi Critici</Text>
                <Form.Item name="notify_critical_alarms" valuePropName="checked" noStyle>
                  <Switch />
                </Form.Item>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Avvisi</Text>
                <Form.Item name="notify_warnings" valuePropName="checked" noStyle>
                  <Switch />
                </Form.Item>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Report Giornaliero</Text>
                <Form.Item name="notify_daily_report" valuePropName="checked" noStyle>
                  <Switch />
                </Form.Item>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Report Settimanale</Text>
                <Form.Item name="notify_weekly_report" valuePropName="checked" noStyle>
                  <Switch />
                </Form.Item>
              </div>
            </Space>
          </Card>

          <Card title="Soglie Allarme" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Batteria Bassa (%)" name="battery_low_threshold">
                  <InputNumber min={5} max={50} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Batteria Critica (%)" name="battery_critical_threshold">
                  <InputNumber min={1} max={20} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        </Form>
      ),
    },
    {
      key: 'devices',
      label: (
        <span>
          <ThunderboltOutlined />
          Dispositivi
        </span>
      ),
      children: (
        <div>
          <Card 
            title="Dispositivi Configurati" 
            size="small" 
            style={{ marginBottom: 16 }}
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                size="small" 
                onClick={() => refetchDevices()}
                loading={devicesLoading}
              >
                Aggiorna
              </Button>
            }
          >
            {devicesLoading ? (
              <Skeleton active paragraph={{ rows: 2 }} />
            ) : devices.length === 0 ? (
              <Alert message="Nessun dispositivo configurato" type="info" />
            ) : (
              <Space direction="vertical" style={{ width: '100%' }}>
                {devices.map((device) => (
                  <Card key={device.thing_key} size="small" style={{ marginBottom: 8 }}>
                    <Descriptions column={2} size="small">
                      <Descriptions.Item label="Thing Key">
                        <Text code>{device.thing_key}</Text>
                      </Descriptions.Item>
                      <Descriptions.Item label="Tipo">{device.device_type}</Descriptions.Item>
                      <Descriptions.Item label="Stato">
                        <Tag color={getStatusColor(device.status)}>
                          {device.status === 'online' ? 'Online' : 
                           device.status === 'offline' ? 'Offline' : 'Sconosciuto'}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="Ultimo Aggiornamento">
                        {device.last_update || 'N/A'}
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                ))}
              </Space>
            )}
          </Card>

          <Card title="Aggiungi Dispositivo" size="small">
            <Form layout="vertical">
              <Form.Item 
                label="Thing Key" 
                name="new_thing_key"
                help="Codice identificativo del dispositivo ZCS"
              >
                <Input placeholder="Es: ZE1ESXXXXXX" />
              </Form.Item>
              <Button type="primary" disabled>
                Aggiungi Dispositivo
              </Button>
              <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                Per aggiungere nuovi dispositivi, contattare l'amministratore.
              </Text>
            </Form>
          </Card>
        </div>
      ),
    },
    {
      key: 'api',
      label: (
        <span>
          <ApiOutlined />
          API
        </span>
      ),
      children: (
        <div>
          <Card 
            title="Configurazione ZCS API" 
            size="small" 
            style={{ marginBottom: 16 }}
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                size="small" 
                onClick={() => refetchApiStatus()}
                loading={apiLoading}
              >
                Verifica
              </Button>
            }
          >
            {apiLoading ? (
              <Skeleton active paragraph={{ rows: 3 }} />
            ) : apiStatus ? (
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Endpoint">
                  <Text code>{apiStatus.endpoint}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Client Code">
                  {apiStatus.client_code_configured ? (
                    <Tag color="green"><CheckCircleOutlined /> Configurato</Tag>
                  ) : (
                    <Tag color="red"><CloseCircleOutlined /> Non configurato</Tag>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="Stato Connessione">
                  {apiStatus.connected ? (
                    <Tag color="green"><CheckCircleOutlined /> Connesso</Tag>
                  ) : (
                    <Tag color="red"><CloseCircleOutlined /> Disconnesso</Tag>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="Ultimo Sync">
                  {apiStatus.last_sync || 'Mai'}
                </Descriptions.Item>
                {apiStatus.error && (
                  <Descriptions.Item label="Errore">
                    <Text type="danger">{apiStatus.error}</Text>
                  </Descriptions.Item>
                )}
              </Descriptions>
            ) : (
              <Alert message="Impossibile recuperare lo stato API" type="warning" />
            )}
          </Card>

          <Card title="Intervalli di Aggiornamento" size="small">
            <Form form={form} layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Dati Real-time (secondi)" name="realtime_interval">
                    <InputNumber min={10} max={300} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Dati Storici (minuti)" name="historical_interval">
                    <InputNumber min={5} max={60} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </div>
      ),
    },
    {
      key: 'system',
      label: (
        <span>
          <DatabaseOutlined />
          Sistema
        </span>
      ),
      children: (
        <div>
          <Card title="Informazioni Sistema" size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="Versione">v2.0.0</Descriptions.Item>
              <Descriptions.Item label="Build">2025-01-01</Descriptions.Item>
              <Descriptions.Item label="Backend">FastAPI + Auth0</Descriptions.Item>
              <Descriptions.Item label="Frontend">React + Refine</Descriptions.Item>
              <Descriptions.Item label="Database">PostgreSQL + InfluxDB</Descriptions.Item>
              <Descriptions.Item label="Cache">Redis</Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="Manutenzione" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button icon={<DatabaseOutlined />} block disabled>
                Backup Database
              </Button>
              <Button icon={<SecurityScanOutlined />} block disabled>
                Verifica Integrità
              </Button>
              <Text type="secondary">
                Funzionalità di manutenzione disponibili solo per amministratori.
              </Text>
            </Space>
          </Card>
        </div>
      ),
    },
  ];

  if (isError) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="Errore"
          description="Impossibile caricare le impostazioni. Riprova più tardi."
          type="error"
          showIcon
        />
      </div>
    );
  }

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            <SettingOutlined /> Impostazioni
          </Title>
          <Text type="secondary">
            Configurazione del sistema e preferenze utente
          </Text>
        </div>
        
        <Button 
          type="primary" 
          icon={isUpdating ? <LoadingOutlined /> : <SaveOutlined />}
          loading={isUpdating}
          onClick={handleSave}
          disabled={isLoading}
        >
          Salva Modifiche
        </Button>
      </div>

      <Card>
        <Tabs items={tabItems} />
      </Card>
    </div>
  );
};

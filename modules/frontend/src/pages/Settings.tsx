import React, { useState } from 'react';
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
  message,
  Tabs,
  Descriptions,
  Tag
} from 'antd';
import { 
  SettingOutlined,
  UserOutlined,
  BellOutlined,
  ThunderboltOutlined,
  SaveOutlined,
  ApiOutlined,
  DatabaseOutlined,
  SecurityScanOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

export const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSave = async () => {
    try {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simula salvataggio
      message.success('Impostazioni salvate con successo!');
    } catch (error) {
      message.error('Errore nel salvataggio delle impostazioni');
    } finally {
      setLoading(false);
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
      children: (
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            system_name: 'Casa Tommasini',
            language: 'it',
            timezone: 'Europe/Rome',
            energy_price: 0.25,
            sell_price: 0.10,
            currency: 'EUR',
          }}
        >
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
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Valuta" name="currency">
                <Select>
                  <Option value="EUR">Euro (€)</Option>
                  <Option value="USD">US Dollar ($)</Option>
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
      children: (
        <Form layout="vertical">
          <Card title="Notifiche Email" size="small" style={{ marginBottom: 16 }}>
            <Form.Item label="Email" name="notification_email">
              <Input placeholder="email@esempio.com" />
            </Form.Item>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Allarmi Critici</Text>
                <Switch defaultChecked />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Avvisi</Text>
                <Switch defaultChecked />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Report Giornaliero</Text>
                <Switch />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text>Report Settimanale</Text>
                <Switch defaultChecked />
              </div>
            </Space>
          </Card>

          <Card title="Soglie Allarme" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Batteria Bassa (%)" name="battery_low_threshold">
                  <InputNumber min={5} max={50} defaultValue={20} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Batteria Critica (%)" name="battery_critical_threshold">
                  <InputNumber min={1} max={20} defaultValue={10} style={{ width: '100%' }} />
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
          <Card title="Dispositivi Configurati" size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="Thing Key">ZE1ES330J9E558</Descriptions.Item>
              <Descriptions.Item label="Tipo">Inverter Ibrido</Descriptions.Item>
              <Descriptions.Item label="Stato">
                <Tag color="green">Online</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Ultimo Aggiornamento">Ora</Descriptions.Item>
            </Descriptions>
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
          <Card title="Configurazione ZCS API" size="small" style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Endpoint">
                https://third.zcsazzurroportal.com:19003/
              </Descriptions.Item>
              <Descriptions.Item label="Client Code">
                <Text code>••••••••</Text>
              </Descriptions.Item>
              <Descriptions.Item label="Stato Connessione">
                <Tag color="green">Connesso</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Ultimo Sync">
                Pochi secondi fa
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="Intervalli di Aggiornamento" size="small">
            <Form layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Dati Real-time (secondi)">
                    <InputNumber min={10} max={300} defaultValue={60} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Dati Storici (minuti)">
                    <InputNumber min={5} max={60} defaultValue={15} style={{ width: '100%' }} />
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
              <Descriptions.Item label="Build">2025-12-12</Descriptions.Item>
              <Descriptions.Item label="Backend">FastAPI</Descriptions.Item>
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
          icon={<SaveOutlined />}
          loading={loading}
          onClick={handleSave}
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

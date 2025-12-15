import React, { useState, useMemo } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Table, 
  Tag, 
  Typography, 
  Space, 
  Button,
  Segmented,
  Badge,
  Empty,
  Statistic,
  Alert
} from 'antd';
import { 
  BellOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  FilterOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import { formatRelativeTime } from '@/utils/formatters';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

type AlarmSeverity = 'critical' | 'warning' | 'info';
type AlarmStatus = 'active' | 'acknowledged' | 'resolved';

interface Alarm {
  id: string;
  device_id: string;
  device_name: string;
  code: string;
  message: string;
  severity: AlarmSeverity;
  status: AlarmStatus;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

// Dati mock per demo (in produzione verrebbero dall'API)
const mockAlarms: Alarm[] = [
  {
    id: '1',
    device_id: 'ZE1ES330J9E558',
    device_name: 'Inverter ZCS 1',
    code: 'W001',
    message: 'Batteria sotto il 20%',
    severity: 'warning',
    status: 'active',
    created_at: dayjs().subtract(2, 'hour').toISOString(),
  },
  {
    id: '2',
    device_id: 'ZE1ES330J9E558',
    device_name: 'Inverter ZCS 1',
    code: 'I001',
    message: 'Produzione solare inferiore alla media',
    severity: 'info',
    status: 'acknowledged',
    created_at: dayjs().subtract(1, 'day').toISOString(),
    acknowledged_at: dayjs().subtract(20, 'hour').toISOString(),
  },
  {
    id: '3',
    device_id: 'ZE1ES330J9E558',
    device_name: 'Inverter ZCS 1',
    code: 'I002',
    message: 'Manutenzione programmata completata',
    severity: 'info',
    status: 'resolved',
    created_at: dayjs().subtract(3, 'day').toISOString(),
    resolved_at: dayjs().subtract(2, 'day').toISOString(),
  },
];

export const Alarms: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('all');
  const [alarms] = useState<Alarm[]>(mockAlarms);

  const filteredAlarms = useMemo(() => {
    if (filter === 'all') return alarms;
    if (filter === 'active') return alarms.filter(a => a.status === 'active' || a.status === 'acknowledged');
    return alarms.filter(a => a.status === 'resolved');
  }, [alarms, filter]);

  const stats = useMemo(() => ({
    total: alarms.length,
    active: alarms.filter(a => a.status === 'active').length,
    acknowledged: alarms.filter(a => a.status === 'acknowledged').length,
    resolved: alarms.filter(a => a.status === 'resolved').length,
    critical: alarms.filter(a => a.severity === 'critical' && a.status === 'active').length,
    warning: alarms.filter(a => a.severity === 'warning' && a.status === 'active').length,
  }), [alarms]);

  const getSeverityTag = (severity: AlarmSeverity) => {
    switch (severity) {
      case 'critical':
        return <Tag color="error" icon={<CloseCircleOutlined />}>Critico</Tag>;
      case 'warning':
        return <Tag color="warning" icon={<WarningOutlined />}>Attenzione</Tag>;
      case 'info':
        return <Tag color="blue" icon={<ExclamationCircleOutlined />}>Info</Tag>;
    }
  };

  const getStatusTag = (status: AlarmStatus) => {
    switch (status) {
      case 'active':
        return <Tag color="red">Attivo</Tag>;
      case 'acknowledged':
        return <Tag color="orange">Preso in carico</Tag>;
      case 'resolved':
        return <Tag color="green">Risolto</Tag>;
    }
  };

  const columns = [
    {
      title: 'Severità',
      dataIndex: 'severity',
      key: 'severity',
      width: 120,
      render: (severity: AlarmSeverity) => getSeverityTag(severity),
    },
    {
      title: 'Codice',
      dataIndex: 'code',
      key: 'code',
      width: 80,
    },
    {
      title: 'Messaggio',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: 'Dispositivo',
      dataIndex: 'device_name',
      key: 'device_name',
      width: 150,
    },
    {
      title: 'Stato',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (status: AlarmStatus) => getStatusTag(status),
    },
    {
      title: 'Data',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => formatRelativeTime(date),
    },
    {
      title: 'Azioni',
      key: 'actions',
      width: 150,
      render: (_: any, record: Alarm) => (
        <Space size="small">
          {record.status === 'active' && (
            <Button size="small" type="link">
              Conferma
            </Button>
          )}
          {record.status !== 'resolved' && (
            <Button size="small" type="link" style={{ color: '#52c41a' }}>
              Risolvi
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            <BellOutlined /> Allarmi
          </Title>
          <Text type="secondary">
            Gestione allarmi e notifiche del sistema
          </Text>
        </div>
        
        <Space wrap>
          <Button icon={<ReloadOutlined />}>
            Aggiorna
          </Button>
          <Button icon={<HistoryOutlined />}>
            Storico
          </Button>
        </Space>
      </div>

      {/* Alert attivi */}
      {stats.critical > 0 && (
        <Alert
          message={`${stats.critical} allarme critico attivo!`}
          description="Richiede attenzione immediata."
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Allarmi Attivi"
              value={stats.active}
              valueStyle={{ color: stats.active > 0 ? '#ff4d4f' : '#52c41a' }}
              prefix={stats.active > 0 ? <WarningOutlined /> : <CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="In Attesa"
              value={stats.acknowledged}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Risolti Oggi"
              value={stats.resolved}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Totale"
              value={stats.total}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtri */}
      <Card 
        title={
          <Space>
            <FilterOutlined />
            <span>Lista Allarmi</span>
          </Space>
        }
        extra={
          <Segmented
            value={filter}
            onChange={(value) => setFilter(value as typeof filter)}
            options={[
              { 
                label: <Badge count={stats.total} size="small" offset={[10, 0]}>Tutti</Badge>, 
                value: 'all' 
              },
              { 
                label: <Badge count={stats.active + stats.acknowledged} size="small" color="red" offset={[10, 0]}>Attivi</Badge>, 
                value: 'active' 
              },
              { 
                label: <Badge count={stats.resolved} size="small" color="green" offset={[10, 0]}>Risolti</Badge>, 
                value: 'resolved' 
              },
            ]}
          />
        }
      >
        {filteredAlarms.length === 0 ? (
          <Empty 
            description="Nessun allarme trovato"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Table
            dataSource={filteredAlarms}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            size="small"
            rowClassName={(record) => 
              record.status === 'active' && record.severity === 'critical' 
                ? 'alarm-row-critical' 
                : record.status === 'active' 
                  ? 'alarm-row-active' 
                  : ''
            }
          />
        )}
      </Card>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Table,
  Tag,
  Typography,
  Space,
  Button,
  Input,
  DatePicker,
  Select,
  Modal,
  Descriptions,
  Statistic,
  message,
  Tooltip,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  DownloadOutlined,
  EyeOutlined,
  FilterOutlined,
  ReloadOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import { api } from '@/utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface AuditLog {
  id: number;
  timestamp: string;
  user_id?: string;
  user_email?: string;
  user_name?: string;
  action: string;
  action_category?: string;
  resource_type?: string;
  resource_id?: string;
  method?: string;
  endpoint?: string;
  ip_address?: string;
  user_agent?: string;
  status_code?: number;
  success?: string;
  duration_ms?: number;
  error_message?: string;
  request_data?: any;
  response_data?: any;
  metadata?: any;
}

interface AuditStats {
  total_logs: number;
  unique_users: number;
  actions_by_type: Record<string, number>;
  actions_by_category: Record<string, number>;
  success_rate: number;
  period_start: string;
  period_end: string;
}

export const Audit: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  // Filtri
  const [filters, setFilters] = useState({
    user_email: '',
    action: '',
    action_category: '',
    success: '',
    date_range: null as [Dayjs, Dayjs] | null,
  });

  // Fetch logs
  const fetchLogs = async (page = 1, size = pageSize) => {
    setLoading(true);
    try {
      const params: any = {
        limit: size,
        offset: (page - 1) * size,
        sort_by: 'timestamp',
        sort_order: 'desc',
      };

      // Applica filtri
      if (filters.user_email) params.user_email = filters.user_email;
      if (filters.action) params.action = filters.action;
      if (filters.action_category) params.action_category = filters.action_category;
      if (filters.success) params.success = filters.success;
      if (filters.date_range) {
        params.date_from = filters.date_range[0].toISOString();
        params.date_to = filters.date_range[1].toISOString();
      }

      const response = await api.get('/api/v1/audit/', { params });
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      console.error('Error fetching audit logs:', error);
      message.error('Errore nel caricamento dei log di audit');
    } finally {
      setLoading(false);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const params: any = {};
      if (filters.date_range) {
        params.date_from = filters.date_range[0].toISOString();
        params.date_to = filters.date_range[1].toISOString();
      }

      const response = await api.get('/api/v1/audit/stats/summary', { params });
      setStats(response.data);
    } catch (error: any) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchLogs(currentPage, pageSize);
    fetchStats();
  }, []);

  // Handle filter change
  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Apply filters
  const applyFilters = () => {
    setCurrentPage(1);
    fetchLogs(1, pageSize);
    fetchStats();
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      user_email: '',
      action: '',
      action_category: '',
      success: '',
      date_range: null,
    });
    setCurrentPage(1);
    fetchLogs(1, pageSize);
    fetchStats();
  };

  // Export CSV
  const exportCSV = async () => {
    try {
      message.loading({ content: 'Esportazione in corso...', key: 'export' });

      const params: any = {
        limit: 10000,
      };

      // Applica filtri
      if (filters.user_email) params.user_email = filters.user_email;
      if (filters.action) params.action = filters.action;
      if (filters.action_category) params.action_category = filters.action_category;
      if (filters.success) params.success = filters.success;
      if (filters.date_range) {
        params.date_from = filters.date_range[0].toISOString();
        params.date_to = filters.date_range[1].toISOString();
      }

      const response = await api.get('/api/v1/audit/export/csv', {
        params,
        responseType: 'blob',
      });

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_logs_${dayjs().format('YYYYMMDD_HHmmss')}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success({ content: 'Export completato!', key: 'export' });
    } catch (error: any) {
      console.error('Error exporting CSV:', error);
      message.error({ content: 'Errore durante l\'export', key: 'export' });
    }
  };

  // Export JSON
  const exportJSON = async () => {
    try {
      message.loading({ content: 'Esportazione in corso...', key: 'export' });

      const params: any = {
        limit: 10000,
      };

      // Applica filtri
      if (filters.user_email) params.user_email = filters.user_email;
      if (filters.action) params.action = filters.action;
      if (filters.action_category) params.action_category = filters.action_category;
      if (filters.success) params.success = filters.success;
      if (filters.date_range) {
        params.date_from = filters.date_range[0].toISOString();
        params.date_to = filters.date_range[1].toISOString();
      }

      const response = await api.get('/api/v1/audit/export/json', {
        params,
        responseType: 'blob',
      });

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_logs_${dayjs().format('YYYYMMDD_HHmmss')}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success({ content: 'Export completato!', key: 'export' });
    } catch (error: any) {
      console.error('Error exporting JSON:', error);
      message.error({ content: 'Errore durante l\'export', key: 'export' });
    }
  };

  // Show detail modal
  const showDetailModal = (log: AuditLog) => {
    setSelectedLog(log);
    setModalVisible(true);
  };

  // Success badge
  const getSuccessBadge = (success?: string) => {
    switch (success) {
      case 'success':
        return <Tag color="success" icon={<CheckCircleOutlined />}>Successo</Tag>;
      case 'failure':
        return <Tag color="warning" icon={<WarningOutlined />}>Fallimento</Tag>;
      case 'error':
        return <Tag color="error" icon={<CloseCircleOutlined />}>Errore</Tag>;
      default:
        return <Tag>N/A</Tag>;
    }
  };

  // Action category color
  const getCategoryColor = (category?: string) => {
    const colors: Record<string, string> = {
      auth: 'blue',
      device: 'green',
      alarm: 'red',
      data: 'purple',
      settings: 'orange',
      api: 'cyan',
      audit: 'magenta',
    };
    return colors[category || ''] || 'default';
  };

  // Table columns
  const columns: ColumnsType<AuditLog> = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => (
        <Tooltip title={dayjs(timestamp).format('DD/MM/YYYY HH:mm:ss')}>
          <Text>{dayjs(timestamp).format('HH:mm:ss')}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {dayjs(timestamp).format('DD/MM/YYYY')}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: 'Utente',
      key: 'user',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{record.user_name || record.user_email || 'System'}</Text>
          {record.user_email && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.user_email}
            </Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Azione',
      dataIndex: 'action',
      key: 'action',
      width: 150,
      render: (action: string) => <Tag>{action}</Tag>,
    },
    {
      title: 'Categoria',
      dataIndex: 'action_category',
      key: 'action_category',
      width: 120,
      render: (category?: string) =>
        category ? <Tag color={getCategoryColor(category)}>{category}</Tag> : '-',
    },
    {
      title: 'Risorsa',
      key: 'resource',
      width: 150,
      render: (_, record) =>
        record.resource_type ? (
          <Space direction="vertical" size={0}>
            <Text strong>{record.resource_type}</Text>
            {record.resource_id && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {record.resource_id}
              </Text>
            )}
          </Space>
        ) : (
          '-'
        ),
    },
    {
      title: 'Endpoint',
      dataIndex: 'endpoint',
      key: 'endpoint',
      width: 250,
      ellipsis: true,
      render: (endpoint?: string, record?: AuditLog) => (
        <Tooltip title={endpoint}>
          <Tag color="default">
            {record?.method} {endpoint}
          </Tag>
        </Tooltip>
      ),
    },
    {
      title: 'IP',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 130,
      render: (ip?: string) => <Text code>{ip || '-'}</Text>,
    },
    {
      title: 'Status',
      key: 'status',
      width: 120,
      align: 'center',
      render: (_, record) => (
        <Space direction="vertical" size={0} style={{ width: '100%' }}>
          {getSuccessBadge(record.success)}
          {record.status_code && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.status_code}
            </Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Durata',
      dataIndex: 'duration_ms',
      key: 'duration_ms',
      width: 100,
      align: 'right',
      render: (duration?: number) =>
        duration ? <Text>{duration}ms</Text> : '-',
    },
    {
      title: 'Azioni',
      key: 'actions',
      width: 80,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => showDetailModal(record)}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Title level={2} style={{ margin: 0 }}>
              Audit Log
            </Title>
            <Space>
              <Button
                icon={<DownloadOutlined />}
                onClick={exportCSV}
              >
                Export CSV
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={exportJSON}
              >
                Export JSON
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  fetchLogs(currentPage, pageSize);
                  fetchStats();
                }}
              >
                Ricarica
              </Button>
            </Space>
          </Space>
        </Col>
      </Row>

      {/* Stats */}
      {stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Totale Log"
                value={stats.total_logs}
                prefix={<ClockCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Utenti Unici"
                value={stats.unique_users}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Success Rate"
                value={stats.success_rate}
                suffix="%"
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: stats.success_rate >= 90 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Categorie"
                value={Object.keys(stats.actions_by_category).length}
                prefix={<FilterOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="Email utente"
              prefix={<SearchOutlined />}
              value={filters.user_email}
              onChange={(e) => handleFilterChange('user_email', e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="Azione"
              value={filters.action}
              onChange={(e) => handleFilterChange('action', e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Categoria"
              style={{ width: '100%' }}
              value={filters.action_category || undefined}
              onChange={(value) => handleFilterChange('action_category', value)}
              allowClear
            >
              <Option value="auth">Auth</Option>
              <Option value="device">Device</Option>
              <Option value="alarm">Alarm</Option>
              <Option value="data">Data</Option>
              <Option value="settings">Settings</Option>
              <Option value="api">API</Option>
              <Option value="audit">Audit</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Esito"
              style={{ width: '100%' }}
              value={filters.success || undefined}
              onChange={(value) => handleFilterChange('success', value)}
              allowClear
            >
              <Option value="success">Successo</Option>
              <Option value="failure">Fallimento</Option>
              <Option value="error">Errore</Option>
            </Select>
          </Col>
          <Col xs={24} md={12}>
            <RangePicker
              style={{ width: '100%' }}
              value={filters.date_range}
              onChange={(dates) => handleFilterChange('date_range', dates)}
              showTime
              format="DD/MM/YYYY HH:mm"
            />
          </Col>
          <Col xs={24} md={12}>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={applyFilters}
              >
                Cerca
              </Button>
              <Button onClick={resetFilters}>Reset</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={logs}
          loading={loading}
          rowKey="id"
          scroll={{ x: 1500 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Totale ${total} log`,
            pageSizeOptions: ['10', '25', '50', '100'],
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
              fetchLogs(page, size);
            },
          }}
        />
      </Card>

      {/* Detail Modal */}
      <Modal
        title={`Dettaglio Audit Log #${selectedLog?.id}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Chiudi
          </Button>,
        ]}
        width={800}
      >
        {selectedLog && (
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label="Timestamp">
              {dayjs(selectedLog.timestamp).format('DD/MM/YYYY HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="Utente">
              {selectedLog.user_name || selectedLog.user_email || 'System'}
            </Descriptions.Item>
            <Descriptions.Item label="Email">
              {selectedLog.user_email || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="User ID">
              {selectedLog.user_id || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="Azione">
              <Tag>{selectedLog.action}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Categoria">
              {selectedLog.action_category ? (
                <Tag color={getCategoryColor(selectedLog.action_category)}>
                  {selectedLog.action_category}
                </Tag>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Tipo Risorsa">
              {selectedLog.resource_type || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="ID Risorsa">
              {selectedLog.resource_id || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="Method">{selectedLog.method || '-'}</Descriptions.Item>
            <Descriptions.Item label="Endpoint">
              <Text code>{selectedLog.endpoint || '-'}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="IP Address">
              <Text code>{selectedLog.ip_address || '-'}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="User Agent">
              <Text ellipsis style={{ maxWidth: 600 }}>
                {selectedLog.user_agent || '-'}
              </Text>
            </Descriptions.Item>
            <Descriptions.Item label="Status Code">
              {selectedLog.status_code || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="Esito">
              {getSuccessBadge(selectedLog.success)}
            </Descriptions.Item>
            <Descriptions.Item label="Durata">
              {selectedLog.duration_ms ? `${selectedLog.duration_ms}ms` : '-'}
            </Descriptions.Item>
            {selectedLog.error_message && (
              <Descriptions.Item label="Errore">
                <Text type="danger">{selectedLog.error_message}</Text>
              </Descriptions.Item>
            )}
            {selectedLog.request_data && (
              <Descriptions.Item label="Request Data">
                <pre style={{ maxHeight: 200, overflow: 'auto', fontSize: 12 }}>
                  {JSON.stringify(selectedLog.request_data, null, 2)}
                </pre>
              </Descriptions.Item>
            )}
            {selectedLog.response_data && (
              <Descriptions.Item label="Response Data">
                <pre style={{ maxHeight: 200, overflow: 'auto', fontSize: 12 }}>
                  {JSON.stringify(selectedLog.response_data, null, 2)}
                </pre>
              </Descriptions.Item>
            )}
            {selectedLog.metadata && (
              <Descriptions.Item label="Metadata">
                <pre style={{ maxHeight: 200, overflow: 'auto', fontSize: 12 }}>
                  {JSON.stringify(selectedLog.metadata, null, 2)}
                </pre>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

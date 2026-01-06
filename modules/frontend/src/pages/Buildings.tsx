/**
 * Buildings Page
 * 
 * Pagina completa per la gestione degli edifici:
 * - Lista edifici con card
 * - Modifica nome/indirizzo
 * - Gestione membri (invita/rimuovi)
 * - Gestione dispositivi associati
 */

import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Button,
  Typography,
  Space,
  Empty,
  Spin,
  Tabs,
  Tag,
  Statistic,
  Modal,
  Form,
  Input,
  Select,
  Table,
  message,
  Popconfirm,
  Tooltip,
} from 'antd';
import {
  HomeOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EnvironmentOutlined,
  CloudOutlined,
  ThunderboltOutlined,
  UserAddOutlined,
  UserDeleteOutlined,
  TeamOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useBuildings, useUpdateBuilding, useDeleteBuilding } from '@/hooks/useBuildings';
import type { Building } from '@/types/building';
import AddressAutocomplete from '@/components/common/AddressAutocomplete';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

export const Buildings: React.FC = () => {
  const navigate = useNavigate();
  const { data: buildings, isLoading } = useBuildings();
  const updateBuilding = useUpdateBuilding();
  const deleteBuilding = useDeleteBuilding();
  
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [membersModalVisible, setMembersModalVisible] = useState(false);
  const [devicesModalVisible, setDevicesModalVisible] = useState(false);
  const [form] = Form.useForm();

  // Handler creazione edificio
  const handleCreateBuilding = () => {
    navigate('/onboarding/building');
  };

  // Handler edit edificio
  const handleEditBuilding = (building: Building) => {
    setSelectedBuilding(building);
    form.setFieldsValue({
      name: building.name,
      address: building.address,
    });
    setEditModalVisible(true);
  };

  // Handler salvataggio modifiche
  const handleSaveBuilding = async () => {
    try {
      const values = await form.validateFields();
      if (selectedBuilding) {
        await updateBuilding.mutateAsync({
          id: selectedBuilding.id,
          name: values.name,
          address: values.address,
        });
        message.success('Edificio aggiornato con successo');
        setEditModalVisible(false);
        setSelectedBuilding(null);
        form.resetFields();
      }
    } catch (error) {
      console.error('Errore aggiornamento edificio:', error);
      message.error('Errore durante l\'aggiornamento');
    }
  };

  // Handler eliminazione edificio
  const handleDeleteBuilding = async (buildingId: number) => {
    try {
      await deleteBuilding.mutateAsync(buildingId);
      message.success('Edificio eliminato con successo');
    } catch (error) {
      console.error('Errore eliminazione edificio:', error);
      message.error('Errore durante l\'eliminazione');
    }
  };

  // Handler gestione membri
  const handleManageMembers = (building: Building) => {
    setSelectedBuilding(building);
    setMembersModalVisible(true);
  };

  // Handler gestione dispositivi
  const handleManageDevices = (building: Building) => {
    setSelectedBuilding(building);
    setDevicesModalVisible(true);
  };

  if (isLoading) {
    return (
      <div style={{ padding: 24, textAlign: 'center', minHeight: 'calc(100vh - 64px)' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24, backgroundColor: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            <HomeOutlined /> Gestione Edifici
          </Title>
          <Text type="secondary">
            Gestisci i tuoi edifici, membri e dispositivi
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={handleCreateBuilding}
        >
          Nuovo Edificio
        </Button>
      </div>

      {/* Lista Edifici */}
      {!buildings || buildings.length === 0 ? (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Nessun edificio configurato"
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateBuilding}>
              Crea il tuo primo edificio
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {buildings.map((building) => (
            <Col xs={24} md={12} lg={8} key={building.id}>
              <Card
                hoverable
                actions={[
                  <Tooltip title="Modifica">
                    <EditOutlined key="edit" onClick={() => handleEditBuilding(building)} />
                  </Tooltip>,
                  <Tooltip title="Gestisci Membri">
                    <TeamOutlined key="members" onClick={() => handleManageMembers(building)} />
                  </Tooltip>,
                  <Tooltip title="Gestisci Dispositivi">
                    <ThunderboltOutlined key="devices" onClick={() => handleManageDevices(building)} />
                  </Tooltip>,
                  <Popconfirm
                    title="Eliminare questo edificio?"
                    description="Questa azione non può essere annullata"
                    onConfirm={() => handleDeleteBuilding(building.id)}
                    okText="Elimina"
                    cancelText="Annulla"
                    okButtonProps={{ danger: true }}
                  >
                    <Tooltip title="Elimina">
                      <DeleteOutlined key="delete" style={{ color: '#ff4d4f' }} />
                    </Tooltip>
                  </Popconfirm>,
                ]}
              >
                <div style={{ marginBottom: 16 }}>
                  <Title level={4} style={{ margin: 0 }}>
                    {building.name}
                  </Title>
                  <Space direction="vertical" size={4} style={{ marginTop: 8, width: '100%' }}>
                    <Space size={4}>
                      <EnvironmentOutlined style={{ color: '#1890ff' }} />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {building.address}
                      </Text>
                    </Space>
                    {building.timezone && (
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        🌍 {building.timezone}
                      </Text>
                    )}
                  </Space>
                </div>

                {/* Meteo Card */}
                {building.current_weather && (
                  <div
                    style={{
                      padding: 12,
                      background: '#e6f7ff',
                      borderRadius: 8,
                      marginBottom: 12,
                    }}
                  >
                    <Row gutter={8} align="middle">
                      <Col span={12}>
                        <Space>
                          <CloudOutlined style={{ fontSize: 20, color: '#1890ff' }} />
                          <div>
                            <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                              {building.current_weather.temperature.toFixed(1)}°C
                            </div>
                            <Text type="secondary" style={{ fontSize: 11 }}>
                              {building.current_weather.weather_condition}
                            </Text>
                          </div>
                        </Space>
                      </Col>
                      <Col span={12}>
                        <div style={{ fontSize: 11 }}>
                          <div>💧 {building.current_weather.humidity}%</div>
                          <div>💨 {building.current_weather.wind_speed?.toFixed(1)} m/s</div>
                        </div>
                      </Col>
                    </Row>
                  </div>
                )}

                {/* Statistiche */}
                <Row gutter={8}>
                  <Col span={12}>
                    <Statistic
                      title="Dispositivi"
                      value={0} // TODO: collegare al count reale
                      prefix={<ThunderboltOutlined />}
                      valueStyle={{ fontSize: 16 }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="Membri"
                      value={1} // TODO: collegare al count reale
                      prefix={<TeamOutlined />}
                      valueStyle={{ fontSize: 16 }}
                    />
                  </Col>
                </Row>

                {/* Tags */}
                <div style={{ marginTop: 12 }}>
                  <Tag color="blue">Proprietario</Tag>
                  {building.created_at && (
                    <Tag>
                      {new Date(building.created_at).toLocaleDateString('it-IT')}
                    </Tag>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* Modal Modifica Edificio */}
      <Modal
        title={
          <Space>
            <EditOutlined />
            <span>Modifica Edificio</span>
          </Space>
        }
        open={editModalVisible}
        onOk={handleSaveBuilding}
        onCancel={() => {
          setEditModalVisible(false);
          setSelectedBuilding(null);
          form.resetFields();
        }}
        okText="Salva"
        cancelText="Annulla"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Nome Edificio"
            name="name"
            rules={[{ required: true, message: 'Inserisci il nome dell\'edificio' }]}
          >
            <Input placeholder="es. Casa Principale, Ufficio, ecc." />
          </Form.Item>

          <Form.Item
            label="Indirizzo"
            name="address"
            rules={[{ required: true, message: 'Inserisci l\'indirizzo' }]}
            tooltip="Per modificare l'indirizzo completo, usa il componente di ricerca"
          >
            <Input placeholder="Via, Città, CAP" disabled />
          </Form.Item>

          <Text type="secondary" style={{ fontSize: 12 }}>
            💡 Per modificare completamente l'indirizzo (con coordinate GPS), elimina e ricrea l'edificio.
          </Text>
        </Form>
      </Modal>

      {/* Modal Gestione Membri */}
      <MembersModal
        visible={membersModalVisible}
        building={selectedBuilding}
        onClose={() => {
          setMembersModalVisible(false);
          setSelectedBuilding(null);
        }}
      />

      {/* Modal Gestione Dispositivi */}
      <DevicesModal
        visible={devicesModalVisible}
        building={selectedBuilding}
        onClose={() => {
          setDevicesModalVisible(false);
          setSelectedBuilding(null);
        }}
      />
    </div>
  );
};

// ============================================================================
// Modal Gestione Membri
// ============================================================================

interface MembersModalProps {
  visible: boolean;
  building: Building | null;
  onClose: () => void;
}

const MembersModal: React.FC<MembersModalProps> = ({ visible, building, onClose }) => {
  const [inviteForm] = Form.useForm();

  // TODO: Implementare chiamate API per membri
  const members = [
    {
      id: '1',
      name: 'Tu',
      email: 'user@example.com',
      role: 'owner',
      joined_at: new Date().toISOString(),
    },
  ];

  const handleInviteMember = async () => {
    try {
      const values = await inviteForm.validateFields();
      // TODO: Chiamata API
      message.success(`Invito inviato a ${values.email}`);
      inviteForm.resetFields();
    } catch (error) {
      console.error('Errore invito membro:', error);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    try {
      // TODO: Chiamata API
      message.success('Membro rimosso con successo');
    } catch (error) {
      console.error('Errore rimozione membro:', error);
    }
  };

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Ruolo',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => {
        const roleColors: Record<string, string> = {
          owner: 'gold',
          admin: 'blue',
          member: 'green',
          viewer: 'default',
        };
        return <Tag color={roleColors[role]}>{role.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Dal',
      dataIndex: 'joined_at',
      key: 'joined_at',
      render: (date: string) => new Date(date).toLocaleDateString('it-IT'),
    },
    {
      title: 'Azioni',
      key: 'actions',
      render: (_: any, record: any) =>
        record.role !== 'owner' && (
          <Popconfirm
            title="Rimuovere questo membro?"
            onConfirm={() => handleRemoveMember(record.id)}
            okText="Rimuovi"
            cancelText="Annulla"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" danger icon={<UserDeleteOutlined />}>
              Rimuovi
            </Button>
          </Popconfirm>
        ),
    },
  ];

  return (
    <Modal
      title={
        <Space>
          <TeamOutlined />
          <span>Gestione Membri - {building?.name}</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <Tabs defaultActiveKey="list">
        <TabPane tab="Lista Membri" key="list">
          <Table
            columns={columns}
            dataSource={members}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </TabPane>

        <TabPane tab="Invita Membro" key="invite">
          <Form form={inviteForm} layout="vertical">
            <Form.Item
              label="Email"
              name="email"
              rules={[
                { required: true, message: 'Inserisci l\'email' },
                { type: 'email', message: 'Email non valida' },
              ]}
            >
              <Input placeholder="email@example.com" />
            </Form.Item>

            <Form.Item
              label="Ruolo"
              name="role"
              initialValue="member"
              rules={[{ required: true, message: 'Seleziona un ruolo' }]}
            >
              <Select>
                <Select.Option value="admin">Admin - Gestione completa</Select.Option>
                <Select.Option value="member">Member - Visualizzazione e controllo</Select.Option>
                <Select.Option value="viewer">Viewer - Solo visualizzazione</Select.Option>
              </Select>
            </Form.Item>

            <Button type="primary" icon={<UserAddOutlined />} onClick={handleInviteMember} block>
              Invia Invito
            </Button>
          </Form>

          <div style={{ marginTop: 16, padding: 12, background: '#f0f2f5', borderRadius: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              <strong>Nota:</strong> L'utente riceverà un'email con un link di invito.
              Dovrà accettare l'invito per accedere all'edificio.
            </Text>
          </div>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

// ============================================================================
// Modal Gestione Dispositivi
// ============================================================================

interface DevicesModalProps {
  visible: boolean;
  building: Building | null;
  onClose: () => void;
}

const DevicesModal: React.FC<DevicesModalProps> = ({ visible, building, onClose }) => {
  const [associateForm] = Form.useForm();

  // TODO: Fetch devices from API
  const devices = [];

  const handleAssociateDevice = async () => {
    try {
      const values = await associateForm.validateFields();
      // TODO: Chiamata API
      message.success(`Dispositivo ${values.thing_key} associato con successo`);
      associateForm.resetFields();
    } catch (error) {
      console.error('Errore associazione dispositivo:', error);
    }
  };

  const handleRemoveDevice = async (deviceId: string) => {
    try {
      // TODO: Chiamata API
      message.success('Dispositivo rimosso con successo');
    } catch (error) {
      console.error('Errore rimozione dispositivo:', error);
    }
  };

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Tipo',
      dataIndex: 'device_type',
      key: 'device_type',
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: 'Seriale',
      dataIndex: 'thing_key',
      key: 'thing_key',
      render: (key: string) => <Text code>{key}</Text>,
    },
    {
      title: 'Stato',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'online' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Azioni',
      key: 'actions',
      render: (_: any, record: any) => (
        <Popconfirm
          title="Rimuovere questo dispositivo?"
          description="Il dispositivo non sarà più associato a questo edificio"
          onConfirm={() => handleRemoveDevice(record.id)}
          okText="Rimuovi"
          cancelText="Annulla"
          okButtonProps={{ danger: true }}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            Rimuovi
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <Modal
      title={
        <Space>
          <ThunderboltOutlined />
          <span>Gestione Dispositivi - {building?.name}</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={900}
    >
      <Tabs defaultActiveKey="list">
        <TabPane tab="Lista Dispositivi" key="list">
          {devices.length === 0 ? (
            <Empty
              description="Nessun dispositivo associato"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Text type="secondary">
                Associa un dispositivo usando la tab "Associa Dispositivo"
              </Text>
            </Empty>
          ) : (
            <Table
              columns={columns}
              dataSource={devices}
              rowKey="id"
              pagination={false}
              size="small"
            />
          )}
        </TabPane>

        <TabPane tab="Associa Dispositivo" key="associate">
          <Form form={associateForm} layout="vertical">
            <Form.Item
              label="Chiave Dispositivo (Thing Key)"
              name="thing_key"
              rules={[{ required: true, message: 'Inserisci la chiave del dispositivo' }]}
              tooltip="La chiave univoca del dispositivo, es. ZE1ES330J9E558"
            >
              <Input placeholder="ZE1ES330J9E558" />
            </Form.Item>

            <Form.Item
              label="Nome Personalizzato"
              name="name"
              rules={[{ required: true, message: 'Inserisci un nome per il dispositivo' }]}
            >
              <Input placeholder="es. Inverter Principale, Pannello Sud, ecc." />
            </Form.Item>

            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAssociateDevice}
              block
            >
              Associa Dispositivo
            </Button>
          </Form>

          <div style={{ marginTop: 16, padding: 12, background: '#f0f2f5', borderRadius: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              <strong>Nota:</strong> Il dispositivo deve essere già configurato e online
              per poterlo associare a questo edificio.
            </Text>
          </div>
        </TabPane>
      </Tabs>
    </Modal>
  );
};


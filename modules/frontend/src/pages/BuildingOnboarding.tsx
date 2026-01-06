/**
 * BuildingOnboarding Page
 * 
 * Pagina per la creazione del primo edificio
 * Mostrata agli utenti che non hanno ancora edifici configurati
 */

import React, { useState } from 'react';
import { Card, Form, Input, Button, Typography, Space, Alert, message } from 'antd';
import { HomeOutlined, EnvironmentOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import AddressAutocomplete from '../components/common/AddressAutocomplete';
import { useCreateBuilding } from '../hooks/useBuildings';
import type { AddressDetailsResponse } from '../types/building';

const { Title, Paragraph, Text } = Typography;

const BuildingOnboarding: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const createBuilding = useCreateBuilding();
  
  const [addressDetails, setAddressDetails] = useState<AddressDetailsResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handler cambio indirizzo
  const handleAddressChange = (address: string, details: AddressDetailsResponse | null) => {
    setAddressDetails(details);
    form.setFieldsValue({ address });
  };

  // Handler submit form
  const handleSubmit = async (values: any) => {
    if (!addressDetails) {
      message.error('Seleziona un indirizzo dalla lista');
      return;
    }

    setIsSubmitting(true);

    try {
      await createBuilding.mutateAsync({
        name: values.name,
        address: addressDetails.formatted_address,
        address_components: addressDetails.address_components,
        place_id: addressDetails.place_id,
        latitude: addressDetails.latitude,
        longitude: addressDetails.longitude,
        timezone: addressDetails.timezone,
      });

      message.success('Edificio creato con successo!');
      
      // Redirect alla dashboard
      setTimeout(() => {
        navigate('/');
      }, 1000);
    } catch (error: any) {
      console.error('Errore creazione edificio:', error);
      message.error(error.response?.data?.message || 'Errore durante la creazione dell\'edificio');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
    >
      <Card
        style={{
          maxWidth: 700,
          width: '100%',
          borderRadius: 16,
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <HomeOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          <Title level={2} style={{ marginBottom: 8 }}>
            Benvenuto in SunPulse! 🌞
          </Title>
          <Paragraph type="secondary" style={{ fontSize: 16 }}>
            Iniziamo configurando il tuo primo edificio
          </Paragraph>
        </div>

        {/* Info Alert */}
        <Alert
          message="Perché serve un edificio?"
          description="L'edificio è l'entità centrale di SunPulse. Qui assoceremo i tuoi dispositivi fotovoltaici e raccoglieremo dati meteo localizzati per analisi più precise."
          type="info"
          showIcon
          icon={<EnvironmentOutlined />}
          style={{ marginBottom: 24 }}
        />

        {/* Form */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          requiredMark="optional"
        >
          {/* Nome Edificio */}
          <Form.Item
            name="name"
            label={
              <Text strong style={{ fontSize: 15 }}>
                Nome Edificio
              </Text>
            }
            rules={[
              { required: true, message: 'Inserisci un nome per l\'edificio' },
              { min: 3, message: 'Il nome deve essere di almeno 3 caratteri' },
              { max: 100, message: 'Il nome non può superare 100 caratteri' },
            ]}
            extra="Es: Casa Principale, Ufficio Milano, Villa al Mare"
          >
            <Input
              size="large"
              placeholder="Casa Principale"
              prefix={<HomeOutlined />}
            />
          </Form.Item>

          {/* Indirizzo */}
          <Form.Item
            name="address"
            label={
              <Text strong style={{ fontSize: 15 }}>
                Indirizzo
              </Text>
            }
            rules={[
              { required: true, message: 'Seleziona un indirizzo' },
            ]}
            extra="Cerca e seleziona l'indirizzo dalla lista. Verrà rilevato automaticamente il timezone."
          >
            <AddressAutocomplete
              onChange={handleAddressChange}
              placeholder="Cerca indirizzo (es: Via Roma 1, Milano)"
              showMap={true}
              mapHeight={250}
            />
          </Form.Item>

          {/* Dettagli Indirizzo Selezionato */}
          {addressDetails && (
            <Alert
              message="Indirizzo Confermato"
              description={
                <Space direction="vertical" size={4}>
                  <Text>
                    <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                    <strong>Coordinate:</strong> {addressDetails.latitude.toFixed(6)}, {addressDetails.longitude.toFixed(6)}
                  </Text>
                  <Text>
                    <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                    <strong>Timezone:</strong> {addressDetails.timezone}
                  </Text>
                </Space>
              }
              type="success"
              showIcon={false}
              style={{ marginBottom: 24 }}
            />
          )}

          {/* Submit Button */}
          <Form.Item style={{ marginBottom: 0, marginTop: 32 }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={isSubmitting}
              disabled={!addressDetails}
              icon={<CheckCircleOutlined />}
            >
              Crea Edificio e Continua
            </Button>
          </Form.Item>
        </Form>

        {/* Footer Note */}
        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            Dopo aver creato l'edificio, potrai aggiungere i tuoi dispositivi fotovoltaici
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default BuildingOnboarding;


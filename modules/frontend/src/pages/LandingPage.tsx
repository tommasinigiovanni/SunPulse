import React from 'react';
import { Button, Typography, Row, Col, Card, Space } from 'antd';
import {
  ThunderboltOutlined,
  BarChartOutlined,
  BellOutlined,
  CloudOutlined,
  SafetyOutlined,
  MobileOutlined,
  ArrowRightOutlined,
  GithubOutlined,
  LinkedinOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface LandingPageProps {
  onLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLogin }) => {
  const features = [
    {
      icon: <ThunderboltOutlined style={{ fontSize: 32, color: '#f5a623' }} />,
      title: 'Monitoraggio Real-Time',
      description: 'Visualizza produzione e consumo energetico in tempo reale con aggiornamenti ogni 2 minuti.',
    },
    {
      icon: <BarChartOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      title: 'Analytics Avanzate',
      description: 'Grafici dettagliati, trend storici e report per ottimizzare il tuo impianto fotovoltaico.',
    },
    {
      icon: <BellOutlined style={{ fontSize: 32, color: '#ff4d4f' }} />,
      title: 'Sistema Allarmi',
      description: 'Notifiche istantanee per anomalie, guasti o cali di produzione del tuo impianto.',
    },
    {
      icon: <CloudOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      title: 'Integrazione ZCS',
      description: 'Connessione diretta con il portale ZCS Azzurro per dati accurati e affidabili.',
    },
    {
      icon: <SafetyOutlined style={{ fontSize: 32, color: '#722ed1' }} />,
      title: 'Sicuro e Privato',
      description: 'Autenticazione Auth0, dati crittografati e accesso protetto alle tue informazioni.',
    },
    {
      icon: <MobileOutlined style={{ fontSize: 32, color: '#13c2c2' }} />,
      title: 'Responsive Design',
      description: 'Accedi da qualsiasi dispositivo: desktop, tablet o smartphone.',
    },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#f5f7fa' }}>
      {/* Header */}
      <header
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid #e8e8e8',
          padding: '12px 24px',
        }}
      >
        <div
          style={{
            maxWidth: 1200,
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <img
              src="/sunpulse-logo.png"
              alt="SunPulse"
              style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              }}
            />
            <span
              style={{
                fontSize: 24,
                fontWeight: 700,
                background: 'linear-gradient(90deg, #f5a623, #1890ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              SunPulse
            </span>
          </div>
          <Space>
            <Button type="primary" size="large" onClick={onLogin}>
              Accedi
            </Button>
          </Space>
        </div>
      </header>

      {/* Hero Section */}
      <section
        style={{
          paddingTop: 120,
          paddingBottom: 80,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background decoration */}
        <div
          style={{
            position: 'absolute',
            top: -100,
            right: -100,
            width: 400,
            height: 400,
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '50%',
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: -50,
            left: -50,
            width: 200,
            height: 200,
            background: 'rgba(255,255,255,0.08)',
            borderRadius: '50%',
          }}
        />

        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', position: 'relative' }}>
          <Row gutter={[48, 48]} align="middle">
            <Col xs={24} md={12}>
              <Title
                level={1}
                style={{
                  color: '#fff',
                  fontSize: 48,
                  fontWeight: 700,
                  marginBottom: 24,
                  lineHeight: 1.2,
                }}
              >
                Monitora il tuo{' '}
                <span style={{ color: '#ffd93d' }}>impianto solare</span> con intelligenza
              </Title>
              <Paragraph
                style={{
                  color: 'rgba(255,255,255,0.9)',
                  fontSize: 18,
                  marginBottom: 32,
                  lineHeight: 1.6,
                }}
              >
                SunPulse è la dashboard definitiva per il monitoraggio del tuo impianto fotovoltaico.
                Analizza produzione, consumo, autoconsumo e risparmio in tempo reale.
              </Paragraph>
              <Space size="middle">
                <Button
                  type="primary"
                  size="large"
                  icon={<ArrowRightOutlined />}
                  onClick={onLogin}
                  style={{
                    height: 50,
                    paddingLeft: 32,
                    paddingRight: 32,
                    fontSize: 16,
                    fontWeight: 600,
                    background: '#f5a623',
                    borderColor: '#f5a623',
                  }}
                >
                  Inizia Ora
                </Button>
                <Button
                  size="large"
                  ghost
                  style={{
                    height: 50,
                    paddingLeft: 32,
                    paddingRight: 32,
                    fontSize: 16,
                    color: '#fff',
                    borderColor: 'rgba(255,255,255,0.5)',
                  }}
                  onClick={() =>
                    window.open('https://github.com/giovannitommasini/sunpulse', '_blank')
                  }
                >
                  <GithubOutlined /> GitHub
                </Button>
              </Space>
            </Col>
            <Col xs={24} md={12}>
              <div
                style={{
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: 16,
                  padding: 24,
                  backdropFilter: 'blur(10px)',
                }}
              >
                <img
                  src="/sunpulse-logo.png"
                  alt="Dashboard Preview"
                  style={{
                    width: '100%',
                    maxWidth: 300,
                    display: 'block',
                    margin: '0 auto',
                    filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.3))',
                  }}
                />
                <div style={{ textAlign: 'center', marginTop: 24 }}>
                  <Title level={3} style={{ color: '#fff', marginBottom: 8 }}>
                    ☀️ Energia Pulita
                  </Title>
                  <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
                    Massimizza l'efficienza del tuo impianto
                  </Text>
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ padding: '60px 24px', background: '#fff' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Row gutter={[32, 32]}>
            <Col xs={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#1890ff', marginBottom: 0 }}>
                  24/7
                </Title>
                <Text type="secondary">Monitoraggio Continuo</Text>
              </div>
            </Col>
            <Col xs={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#52c41a', marginBottom: 0 }}>
                  2 min
                </Title>
                <Text type="secondary">Aggiornamento Dati</Text>
              </div>
            </Col>
            <Col xs={8}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ color: '#f5a623', marginBottom: 0 }}>
                  100%
                </Title>
                <Text type="secondary">Integrazione ZCS</Text>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '80px 24px', background: '#f5f7fa' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 60 }}>
            <Title level={2}>Funzionalità Principali</Title>
            <Paragraph style={{ fontSize: 16, color: '#666', maxWidth: 600, margin: '0 auto' }}>
              Tutto quello che serve per monitorare e ottimizzare il tuo impianto fotovoltaico
            </Paragraph>
          </div>

          <Row gutter={[24, 24]}>
            {features.map((feature, index) => (
              <Col xs={24} sm={12} md={8} key={index}>
                <Card
                  hoverable
                  style={{
                    height: '100%',
                    borderRadius: 12,
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ marginBottom: 16 }}>{feature.icon}</div>
                    <Title level={4} style={{ marginBottom: 8 }}>
                      {feature.title}
                    </Title>
                    <Text type="secondary">{feature.description}</Text>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* CTA Section */}
      <section
        style={{
          padding: '80px 24px',
          background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
          textAlign: 'center',
        }}
      >
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <Title level={2} style={{ color: '#fff', marginBottom: 16 }}>
            Pronto a ottimizzare il tuo impianto?
          </Title>
          <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: 18, marginBottom: 32 }}>
            Accedi ora e inizia a monitorare la produzione del tuo impianto fotovoltaico.
          </Paragraph>
          <Button
            type="primary"
            size="large"
            onClick={onLogin}
            style={{
              height: 56,
              paddingLeft: 48,
              paddingRight: 48,
              fontSize: 18,
              fontWeight: 600,
              background: '#fff',
              color: '#1890ff',
              borderColor: '#fff',
            }}
          >
            Accedi con Auth0
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          padding: '40px 24px',
          background: '#001529',
          color: 'rgba(255,255,255,0.65)',
        }}
      >
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Row gutter={[48, 32]}>
            <Col xs={24} md={8}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <img
                  src="/sunpulse-logo.png"
                  alt="SunPulse"
                  style={{ width: 32, height: 32, borderRadius: '50%' }}
                />
                <span style={{ fontSize: 20, fontWeight: 600, color: '#fff' }}>SunPulse</span>
              </div>
              <Paragraph style={{ color: 'rgba(255,255,255,0.65)' }}>
                Dashboard di monitoraggio per impianti fotovoltaici con integrazione ZCS Azzurro.
              </Paragraph>
            </Col>
            <Col xs={24} md={8}>
              <Title level={5} style={{ color: '#fff' }}>
                Tecnologie
              </Title>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                <li style={{ marginBottom: 8 }}>React + TypeScript</li>
                <li style={{ marginBottom: 8 }}>FastAPI + Python</li>
                <li style={{ marginBottom: 8 }}>PostgreSQL + Redis</li>
                <li style={{ marginBottom: 8 }}>Docker + Traefik</li>
              </ul>
            </Col>
            <Col xs={24} md={8}>
              <Title level={5} style={{ color: '#fff' }}>
                Contatti
              </Title>
              <Space direction="vertical">
                <a
                  href="https://giovannitommasini.it"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: 'rgba(255,255,255,0.65)' }}
                >
                  giovannitommasini.it
                </a>
                <Space>
                  <a
                    href="https://github.com/giovannitommasini"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'rgba(255,255,255,0.65)', fontSize: 20 }}
                  >
                    <GithubOutlined />
                  </a>
                  <a
                    href="https://linkedin.com/in/giovannitommasini"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'rgba(255,255,255,0.65)', fontSize: 20 }}
                  >
                    <LinkedinOutlined />
                  </a>
                </Space>
              </Space>
            </Col>
          </Row>
          <div
            style={{
              borderTop: '1px solid rgba(255,255,255,0.1)',
              marginTop: 40,
              paddingTop: 24,
              textAlign: 'center',
            }}
          >
            <Text style={{ color: 'rgba(255,255,255,0.45)' }}>
              Made with ☀️ by Giovanni Tommasini • © {new Date().getFullYear()} SunPulse
            </Text>
          </div>
        </div>
      </footer>
    </div>
  );
};

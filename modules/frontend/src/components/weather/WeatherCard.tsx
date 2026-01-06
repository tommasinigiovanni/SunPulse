/**
 * WeatherCard Component
 * 
 * Mostra i dati meteo dell'edificio selezionato nella Dashboard
 * Include temperatura, condizioni, umidità e correlazione con produzione energia
 */

import React from 'react';
import { Card, Row, Col, Statistic, Space, Typography, Tooltip, Skeleton } from 'antd';
import {
  CloudOutlined,
  DashboardOutlined,
  DropboxOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  SunOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { BuildingWeather } from '../../types/building';

const { Text, Title } = Typography;

interface WeatherCardProps {
  weather?: BuildingWeather;
  isLoading?: boolean;
  showCorrelation?: boolean;
  currentPower?: number; // Per mostrare correlazione
}

export const WeatherCard: React.FC<WeatherCardProps> = ({
  weather,
  isLoading = false,
  showCorrelation = true,
  currentPower = 0,
}) => {
  if (isLoading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 3 }} />
      </Card>
    );
  }

  if (!weather) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <CloudOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
          <Title level={5} type="secondary" style={{ marginTop: 16 }}>
            Dati meteo non disponibili
          </Title>
          <Text type="secondary">
            Attendi il prossimo aggiornamento meteo
          </Text>
        </div>
      </Card>
    );
  }

  // Icona meteo da OpenWeatherMap
  const weatherIconUrl = weather.weather_icon
    ? `https://openweathermap.org/img/wn/${weather.weather_icon}@2x.png`
    : null;

  // Determina colore temperatura
  const getTempColor = (temp: number) => {
    if (temp < 10) return '#1890ff'; // Freddo
    if (temp < 20) return '#52c41a'; // Mite
    if (temp < 30) return '#faad14'; // Caldo
    return '#ff4d4f'; // Molto caldo
  };

  // Calcola "efficienza teorica" basata su temperatura
  // La produzione fotovoltaica diminuisce con temperature > 25°C
  const getEfficiencyNote = (temp: number) => {
    if (temp < 15) return { icon: <ArrowDownOutlined />, text: 'Temperatura bassa', color: '#1890ff' };
    if (temp < 25) return { icon: <SunOutlined />, text: 'Temperatura ottimale', color: '#52c41a' };
    if (temp < 35) return { icon: <ArrowUpOutlined />, text: 'Temperatura elevata', color: '#faad14' };
    return { icon: <ArrowUpOutlined />, text: 'Temperatura critica', color: '#ff4d4f' };
  };

  const efficiencyNote = getEfficiencyNote(weather.temperature);
  const tempColor = getTempColor(weather.temperature);

  return (
    <Card
      title={
        <Space>
          <CloudOutlined />
          <span>Meteo Edificio</span>
        </Space>
      }
      extra={
        weather.fetched_at && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {new Date(weather.fetched_at).toLocaleTimeString('it-IT', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        )
      }
    >
      <Row gutter={[16, 16]} align="middle">
        {/* Temperatura principale con icona */}
        <Col xs={24} md={12}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {weatherIconUrl && (
              <img
                src={weatherIconUrl}
                alt={weather.weather_condition || 'Meteo'}
                style={{ width: 80, height: 80 }}
              />
            )}
            <div>
              <Statistic
                value={weather.temperature}
                precision={1}
                suffix="°C"
                valueStyle={{ color: tempColor, fontSize: 36 }}
              />
              <Text style={{ fontSize: 14, color: '#666' }}>
                {weather.weather_condition || 'N/D'}
              </Text>
              {weather.feels_like && (
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Percepita: {weather.feels_like.toFixed(1)}°C
                  </Text>
                </div>
              )}
            </div>
          </div>
        </Col>

        {/* Dettagli aggiuntivi */}
        <Col xs={24} md={12}>
          <Space direction="vertical" style={{ width: '100%' }} size={8}>
            {weather.humidity !== undefined && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Space>
                  <DropboxOutlined style={{ color: '#1890ff' }} />
                  <Text>Umidità</Text>
                </Space>
                <Text strong>{weather.humidity}%</Text>
              </div>
            )}

            {weather.wind_speed !== undefined && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Space>
                  <DashboardOutlined style={{ color: '#52c41a' }} />
                  <Text>Vento</Text>
                </Space>
                <Text strong>{weather.wind_speed.toFixed(1)} m/s</Text>
              </div>
            )}

            {weather.pressure !== undefined && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Space>
                  <DashboardOutlined style={{ color: '#faad14' }} />
                  <Text>Pressione</Text>
                </Space>
                <Text strong>{weather.pressure} hPa</Text>
              </div>
            )}
          </Space>
        </Col>

        {/* Correlazione con produzione */}
        {showCorrelation && (
          <Col xs={24}>
            <div
              style={{
                marginTop: 8,
                padding: 12,
                background: `${efficiencyNote.color}15`,
                borderRadius: 8,
                border: `1px solid ${efficiencyNote.color}40`,
              }}
            >
              <Space>
                {efficiencyNote.icon}
                <Text style={{ color: efficiencyNote.color }}>
                  {efficiencyNote.text}
                </Text>
                {currentPower > 0 && (
                  <>
                    <span style={{ color: '#d9d9d9' }}>•</span>
                    <Space size={4}>
                      <ThunderboltOutlined style={{ color: '#1890ff' }} />
                      <Text>
                        Producendo <strong>{currentPower.toFixed(2)} kW</strong>
                      </Text>
                    </Space>
                  </>
                )}
              </Space>
              <div style={{ marginTop: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {weather.temperature < 15 &&
                    'Basse temperature possono ridurre leggermente la produzione.'}
                  {weather.temperature >= 15 &&
                    weather.temperature < 25 &&
                    'Condizioni ideali per la massima efficienza dei pannelli.'}
                  {weather.temperature >= 25 &&
                    weather.temperature < 35 &&
                    'Temperature elevate riducono l\'efficienza dei pannelli (~0.5%/°C sopra i 25°C).'}
                  {weather.temperature >= 35 &&
                    'Temperature critiche: forte riduzione dell\'efficienza dei pannelli.'}
                </Text>
              </div>
            </div>
          </Col>
        )}
      </Row>
    </Card>
  );
};


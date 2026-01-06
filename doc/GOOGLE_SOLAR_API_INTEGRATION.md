# 🌞 Google Solar API - Integration Guide

> **Status:** Pianificato (Fase 4)  
> **Priorità:** Bassa (opzionale, ma ad alto valore aggiunto)  
> **Effort Stimato:** ~14 ore

---

## 📋 Panoramica

La [Google Solar API](https://developers.google.com/maps/documentation/solar/overview?hl=it) fornisce dati dettagliati sul potenziale di energia solare dei tetti degli edifici, basandosi sulle vaste risorse di dati geospaziali di Google.

### Perché Integrarla in SunPulse?

L'integrazione della Solar API permetterebbe di:

1. **Analisi Pre-Installazione**
   - Valutare il potenziale solare prima di installare i pannelli
   - Stimare produzione annuale teorica
   - Calcolare ROI e payback period

2. **Ottimizzazione Impianto**
   - Numero ottimale di pannelli
   - Posizionamento ideale sul tetto
   - Analisi ombreggiamento per stagione

3. **Monitoraggio Performance**
   - Confronto produzione reale vs potenziale teorico
   - Identificazione sottoperformance
   - Alert se produzione < 80% del potenziale

4. **Report e Analytics**
   - Efficienza impianto (% potenziale raggiunto)
   - Suggerimenti miglioramento
   - Previsioni produzione futura

---

## 🎯 Funzionalità Proposte

### 1. Building Insights al Momento della Creazione

Quando l'utente crea un nuovo edificio con indirizzo:

```
┌─────────────────────────────────────────────────┐
│         STEP 2: CREA EDIFICIO                   │
│                                                  │
│  Nome: Casa Principale                          │
│  Indirizzo: Via Roma 1, Milano                  │
│                                                  │
│  📊 POTENZIALE SOLARE                           │
│  ┌─────────────────────────────────────────┐   │
│  │ 🌞 Produzione Stimata: 8,500 kWh/anno   │   │
│  │ 📦 Pannelli Installabili: 25            │   │
│  │ 📐 Area Disponibile: 45.5 m²           │   │
│  │ 💰 Risparmio Annuo: €1,200              │   │
│  │ 📈 ROI: 6.5 anni                        │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  [Crea Edificio e Continua]                    │
└─────────────────────────────────────────────────┘
```

### 2. Dashboard Card "Potenziale vs Reale"

Nella Dashboard principale:

```
┌─────────────────────────────────────────────────┐
│  EFFICIENZA IMPIANTO                             │
│  ┌─────────────────────────────────────────┐   │
│  │ Produzione Oggi: 35.2 kWh               │   │
│  │ Potenziale Teorico: 42.5 kWh            │   │
│  │                                          │   │
│  │ ████████████████░░░░░░ 82.8%            │   │
│  │                                          │   │
│  │ ⚠️ Performance sotto il potenziale       │   │
│  │ Possibile causa: ombreggiamento         │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 3. Analytics - Grafico Confronto

Nella pagina Analytics:

```
┌─────────────────────────────────────────────────┐
│  PRODUZIONE REALE VS POTENZIALE                  │
│                                                  │
│  kWh                                             │
│  50 │                                           │
│     │     ╱╲                                    │
│  40 │    ╱  ╲      ╱╲                          │
│     │   ╱    ╲    ╱  ╲    ╱╲                   │
│  30 │  ╱      ╲  ╱    ╲  ╱  ╲                  │
│     │ ╱        ╲╱      ╲╱    ╲                 │
│  20 │╱                        ╲                 │
│     └────────────────────────────────           │
│      Gen  Feb  Mar  Apr  Mag  Giu               │
│                                                  │
│  ─── Produzione Reale                           │
│  ─ ─ Potenziale Teorico                         │
└─────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints Google Solar

### 1. Building Insights

**Endpoint:** `https://solar.googleapis.com/v1/buildingInsights:findClosest`

**Request:**
```http
GET /v1/buildingInsights:findClosest?location.latitude=45.4642&location.longitude=9.1900&key=API_KEY
```

**Response (esempio):**
```json
{
  "name": "buildings/ChIJ...",
  "center": {
    "latitude": 45.4642,
    "longitude": 9.1900
  },
  "imageryDate": {
    "year": 2023,
    "month": 6,
    "day": 15
  },
  "postalCode": "20121",
  "administrativeArea": "MI",
  "statisticalArea": "Milano",
  "regionCode": "IT",
  "solarPotential": {
    "maxArrayPanelsCount": 25,
    "maxArrayAreaMeters2": 45.5,
    "maxSunshineHoursPerYear": 1850,
    "carbonOffsetFactorKgPerMwh": 428.9,
    "wholeRoofStats": {
      "areaMeters2": 85.2,
      "sunshineQuantiles": [150, 1200, 1400, 1600, 1850],
      "groundAreaMeters2": 80.0
    },
    "roofSegmentStats": [
      {
        "pitchDegrees": 30,
        "azimuthDegrees": 180,
        "stats": {
          "areaMeters2": 45.5,
          "sunshineQuantiles": [200, 1300, 1500, 1700, 1850]
        },
        "center": {
          "latitude": 45.4642,
          "longitude": 9.1900
        },
        "planeHeightAtCenterMeters": 12.5
      }
    ],
    "solarPanelConfigs": [
      {
        "panelsCount": 20,
        "yearlyEnergyDcKwh": 8500,
        "roofSegmentSummaries": [
          {
            "pitchDegrees": 30,
            "azimuthDegrees": 180,
            "panelsCount": 20,
            "yearlyEnergyDcKwh": 8500,
            "segmentIndex": 0
          }
        ]
      }
    ],
    "financialAnalyses": [
      {
        "monthlyBill": {
          "currencyCode": "EUR",
          "units": 100
        },
        "panelConfigIndex": 0,
        "financialDetails": {
          "initialAcKwhPerYear": 8075,
          "remainingLifetimeUtilityBill": {
            "currencyCode": "EUR",
            "units": 15000
          },
          "federalIncentive": {
            "currencyCode": "EUR",
            "units": 2000
          },
          "netMeteringAllowed": true,
          "percentageExportedToGrid": 25.5,
          "solarPercentage": 85.2,
          "costOfElectricityWithoutSolar": {
            "currencyCode": "EUR",
            "units": 30000
          },
          "paybackYears": 6.5,
          "savingsYear1": {
            "currencyCode": "EUR",
            "units": 1200
          },
          "savingsLifetime": {
            "currencyCode": "EUR",
            "units": 24000
          }
        }
      }
    ]
  },
  "imageryQuality": "HIGH",
  "imageryProcessedDate": {
    "year": 2023,
    "month": 7,
    "day": 1
  }
}
```

### 2. Data Layers

**Endpoint:** `https://solar.googleapis.com/v1/dataLayers:get`

Fornisce URL per scaricare layer di dati solari (mappe di irraggiamento, ombreggiatura, ecc.)

### 3. GeoTIFF

**Endpoint:** `https://solar.googleapis.com/v1/geoTiff:get`

Scarica raster con informazioni solari codificate

---

## 🏗️ Architettura Implementazione

### Backend Service

```python
# modules/backend/app/services/google_solar_service.py

from typing import Optional, Dict, Any
import httpx
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class GoogleSolarService:
    """Service per interagire con Google Solar API"""
    
    def __init__(self):
        from app.config.settings import get_settings
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://solar.googleapis.com/v1"
        self.cache_ttl = timedelta(days=90)  # I dati solari cambiano raramente
    
    async def get_building_insights(
        self, 
        latitude: float, 
        longitude: float,
        required_quality: str = "HIGH"
    ) -> Optional[Dict[str, Any]]:
        """
        Ottieni insights sul potenziale solare di un edificio
        
        Args:
            latitude: Latitudine GPS
            longitude: Longitudine GPS
            required_quality: Qualità immagini richiesta (LOW, MEDIUM, HIGH)
            
        Returns:
            Dati potenziale solare o None se non disponibili
        """
        url = f"{self.base_url}/buildingInsights:findClosest"
        params = {
            "location.latitude": latitude,
            "location.longitude": longitude,
            "requiredQuality": required_quality,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 404:
                    logger.warning(
                        "No solar data available",
                        latitude=latitude,
                        longitude=longitude
                    )
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(
                    "Solar insights retrieved",
                    latitude=latitude,
                    longitude=longitude,
                    max_panels=data.get("solarPotential", {}).get("maxArrayPanelsCount")
                )
                
                return data
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(
                "Error fetching solar insights",
                error=str(e),
                status_code=e.response.status_code
            )
            raise
        except Exception as e:
            logger.error("Unexpected error in solar service", error=str(e))
            raise
    
    async def get_solar_panel_config(
        self,
        latitude: float,
        longitude: float,
        panels_count: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ottieni configurazione ottimale pannelli solari
        
        Args:
            latitude: Latitudine GPS
            longitude: Longitudine GPS
            panels_count: Numero desiderato di pannelli (None = max)
            
        Returns:
            Configurazione pannelli ottimale
        """
        insights = await self.get_building_insights(latitude, longitude)
        
        if not insights or "solarPotential" not in insights:
            return None
        
        solar_potential = insights["solarPotential"]
        configs = solar_potential.get("solarPanelConfigs", [])
        
        if not configs:
            return None
        
        # Se non specificato, ritorna la configurazione massima
        if panels_count is None:
            return configs[-1]  # Ultimo = max pannelli
        
        # Trova la configurazione più vicina al numero richiesto
        closest_config = min(
            configs,
            key=lambda c: abs(c["panelsCount"] - panels_count)
        )
        
        return closest_config
    
    def calculate_efficiency(
        self,
        actual_production_kwh: float,
        theoretical_production_kwh: float
    ) -> float:
        """
        Calcola efficienza impianto
        
        Args:
            actual_production_kwh: Produzione reale
            theoretical_production_kwh: Produzione teorica da Solar API
            
        Returns:
            Efficienza in percentuale (0-100)
        """
        if theoretical_production_kwh <= 0:
            return 0.0
        
        return (actual_production_kwh / theoretical_production_kwh) * 100
```

### Backend API Endpoint

```python
# modules/backend/app/api/v1/endpoints/solar.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.services.google_solar_service import GoogleSolarService
from app.services.database import get_db
from app.models.building import Building

router = APIRouter()


@router.get("/buildings/{building_id}/solar-potential")
async def get_building_solar_potential(
    building_id: int,
    db: Session = Depends(get_db)
):
    """Ottieni potenziale solare edificio"""
    
    # Recupera edificio
    building = db.query(Building).filter(Building.id == building_id).first()
    
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    if not building.latitude or not building.longitude:
        raise HTTPException(
            status_code=400, 
            detail="Building has no GPS coordinates"
        )
    
    # Fetch solar data
    solar_service = GoogleSolarService()
    solar_data = await solar_service.get_building_insights(
        latitude=building.latitude,
        longitude=building.longitude
    )
    
    if not solar_data:
        raise HTTPException(
            status_code=404,
            detail="No solar data available for this location"
        )
    
    # Estrai dati principali
    solar_potential = solar_data.get("solarPotential", {})
    
    return {
        "building_id": building_id,
        "building_name": building.name,
        "coordinates": {
            "latitude": building.latitude,
            "longitude": building.longitude
        },
        "imagery_date": solar_data.get("imageryDate"),
        "imagery_quality": solar_data.get("imageryQuality"),
        "solar_potential": {
            "max_panels_count": solar_potential.get("maxArrayPanelsCount"),
            "max_area_m2": solar_potential.get("maxArrayAreaMeters2"),
            "max_sunshine_hours_year": solar_potential.get("maxSunshineHoursPerYear"),
            "carbon_offset_kg_per_mwh": solar_potential.get("carbonOffsetFactorKgPerMwh"),
            "whole_roof_area_m2": solar_potential.get("wholeRoofStats", {}).get("areaMeters2"),
        },
        "recommended_config": solar_potential.get("solarPanelConfigs", [{}])[-1] if solar_potential.get("solarPanelConfigs") else None,
        "financial_analysis": solar_potential.get("financialAnalyses", [{}])[0] if solar_potential.get("financialAnalyses") else None
    }
```

### Frontend Component

```typescript
// modules/frontend/src/components/solar/SolarPotentialCard.tsx

import React from 'react';
import { Card, Statistic, Row, Col, Progress, Alert, Divider } from 'antd';
import { 
  SunOutlined, 
  ThunderboltOutlined, 
  DollarOutlined,
  WarningOutlined 
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface SolarPotentialCardProps {
  buildingId: number;
  actualProductionKwh?: number; // Produzione reale (se disponibile)
}

const SolarPotentialCard: React.FC<SolarPotentialCardProps> = ({
  buildingId,
  actualProductionKwh
}) => {
  const { data: solarData, isLoading } = useQuery({
    queryKey: ['solar-potential', buildingId],
    queryFn: async () => {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/buildings/${buildingId}/solar-potential`
      );
      return response.data;
    },
    staleTime: 7 * 24 * 60 * 60 * 1000, // 7 giorni (dati cambiano raramente)
  });

  if (isLoading) {
    return <Card loading />;
  }

  if (!solarData) {
    return (
      <Card>
        <Alert
          message="Dati Solari Non Disponibili"
          description="Non sono disponibili dati sul potenziale solare per questo edificio."
          type="info"
          showIcon
        />
      </Card>
    );
  }

  const potential = solarData.solar_potential;
  const config = solarData.recommended_config;
  const financial = solarData.financial_analysis;

  // Calcola efficienza se disponibile produzione reale
  const efficiency = actualProductionKwh && config?.yearlyEnergyDcKwh
    ? (actualProductionKwh / config.yearlyEnergyDcKwh) * 100
    : null;

  const isLowEfficiency = efficiency && efficiency < 80;

  return (
    <Card
      title={
        <span>
          <SunOutlined style={{ marginRight: 8 }} />
          Potenziale Solare
        </span>
      }
      extra={
        solarData.imagery_quality === 'HIGH' && (
          <span style={{ color: '#52c41a', fontSize: 12 }}>
            ✓ Alta Qualità
          </span>
        )
      }
    >
      <Row gutter={[16, 16]}>
        {/* Produzione Annuale Stimata */}
        <Col xs={24} sm={12} md={6}>
          <Statistic
            title="Produzione Annuale"
            value={config?.yearlyEnergyDcKwh || 0}
            suffix="kWh"
            prefix={<ThunderboltOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>

        {/* Pannelli Installabili */}
        <Col xs={24} sm={12} md={6}>
          <Statistic
            title="Pannelli Installabili"
            value={potential?.max_panels_count || 0}
            prefix={<SunOutlined />}
            valueStyle={{ color: '#fa8c16' }}
          />
        </Col>

        {/* Risparmio Annuo */}
        {financial?.financialDetails?.savingsYear1 && (
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Risparmio Annuo"
              value={financial.financialDetails.savingsYear1.units}
              suffix={financial.financialDetails.savingsYear1.currencyCode}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
        )}

        {/* Payback Period */}
        {financial?.financialDetails?.paybackYears && (
          <Col xs={24} sm={12} md={6}>
            <Statistic
              title="Ritorno Investimento"
              value={financial.financialDetails.paybackYears}
              suffix="anni"
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
        )}
      </Row>

      {/* Efficienza Impianto (se disponibile) */}
      {efficiency !== null && (
        <>
          <Divider />
          <div>
            <h4>Efficienza Impianto</h4>
            <Progress
              percent={Math.round(efficiency)}
              status={isLowEfficiency ? 'exception' : 'success'}
              strokeColor={isLowEfficiency ? '#ff4d4f' : '#52c41a'}
            />
            {isLowEfficiency && (
              <Alert
                message="Performance Sotto il Potenziale"
                description="L'impianto sta producendo meno del potenziale teorico. Possibili cause: ombreggiamento, sporcizia sui pannelli, o problemi tecnici."
                type="warning"
                showIcon
                icon={<WarningOutlined />}
                style={{ marginTop: 12 }}
              />
            )}
          </div>
        </>
      )}
    </Card>
  );
};

export default SolarPotentialCard;
```

---

## 💰 Costi Google Solar API

| Servizio | Costo per Richiesta |
|----------|---------------------|
| Building Insights | $0.05 |
| Data Layers | $0.05 |
| GeoTIFF | $0.05 |

### Stima Costi per SunPulse

**Scenario: 100 edifici**
- Fetch iniziale building insights: 100 richieste = $5
- Aggiornamento trimestrale: 100 richieste x 4 = $20/anno
- **Totale anno 1:** ~$25

**Con free tier Google Cloud:**
- Credito mensile: $200
- Copertura: ~4,000 richieste/mese
- **Ampiamente coperto dal free tier!**

---

## 📝 Checklist Implementazione

### Backend
- [ ] Creare `GoogleSolarService` in `services/google_solar_service.py`
- [ ] Aggiungere endpoint `/buildings/{id}/solar-potential`
- [ ] Aggiungere endpoint `/buildings/{id}/solar-comparison`
- [ ] Implementare cache per risultati Solar API (TTL: 90 giorni)
- [ ] Gestire gracefully assenza dati (404)

### Frontend
- [ ] Creare componente `SolarPotentialCard`
- [ ] Aggiungere tab "Potenziale Solare" in Building Details
- [ ] Mostrare solar insights in BuildingOnboarding (opzionale)
- [ ] Aggiungere grafico confronto produzione in Analytics

### Documentazione
- [ ] Guida setup Solar API
- [ ] Esempi request/response
- [ ] Best practices caching
- [ ] Gestione errori e fallback

### Testing
- [ ] Test con edifici coperti da Solar API
- [ ] Test con edifici non coperti (404)
- [ ] Test calcolo efficienza
- [ ] Test visualizzazione mobile

---

## 🚀 Valore Aggiunto per SunPulse

L'integrazione Solar API trasformerebbe SunPulse da un sistema di **monitoring** a un sistema di **monitoring + optimization**, offrendo:

1. **Pre-Sales:** Valutazione potenziale prima dell'acquisto
2. **Installazione:** Ottimizzazione posizionamento pannelli
3. **Monitoraggio:** Confronto continuo reale vs teorico
4. **Manutenzione:** Alert automatici per sottoperformance

**Effort vs Value Ratio: MOLTO ALTO** 🌟

---

## 📚 Riferimenti

- [Google Solar API Overview](https://developers.google.com/maps/documentation/solar/overview?hl=it)
- [Building Insights API Reference](https://developers.google.com/maps/documentation/solar/reference/rest/v1/buildingInsights)
- [Data Layers API Reference](https://developers.google.com/maps/documentation/solar/reference/rest/v1/dataLayers)
- [Pricing](https://mapsplatform.google.com/pricing/)

---

*Documento creato il 2026-01-06*


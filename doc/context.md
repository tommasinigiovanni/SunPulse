# ☀️ SunPulse - Context File
> **Data ultimo aggiornamento:** 2025-12-11  
> **Versione progetto:** v2.0.0  
> **Stato:** Fase 2 completata, Fase 3 in corso

---

## 1. Obiettivi del Progetto

Piattaforma di monitoraggio impianti fotovoltaici che integra le API ZCS Azzurro Portal per:
- Visualizzazione dati in tempo reale
- Analisi storiche produzione/consumo
- Gestione allarmi e notifiche
- Automazioni workflow

---

## 2. Stato Attuale

### Fase 1 - Core MVP ✅ COMPLETATA
- [x] Setup infrastructure Docker
- [x] Backend FastAPI con health checks
- [x] Database PostgreSQL e InfluxDB
- [x] Configurazione base servizi

### Fase 2 - Data Integration ✅ COMPLETATA
- [x] ZCS API Service completo (4 endpoint)
- [x] Circuit Breaker per resilienza
- [x] Cache Service multi-layer (Memory L1 + Redis L2)
- [x] Data Collector con Celery
- [x] InfluxDB Writer ottimizzato
- [x] API Endpoints completi (health, devices, data, alarms, tasks)

### Fase 3 - Dashboard Frontend 🔄 IN CORSO
- [x] Setup RefineJS + Ant Design
- [x] Struttura routing base
- [x] Componenti layout (Header)
- [x] DeviceList component
- [x] Dashboard component base
- [x] PowerChart component
- [ ] Device Detail Page
- [ ] Analytics Page
- [ ] Alarms Page
- [ ] Settings Page

### Fase 4 - Production Ready ⏳ NON INIZIATA
- [ ] SSL/HTTPS
- [ ] Performance optimization
- [ ] Monitoring Prometheus/Grafana
- [ ] CI/CD pipeline

---

## 3. Vincoli

### Tecnici
- **API ZCS**: Finestra max 24h per dati storici
- **API ZCS**: Rate limiting ~100 req/ora (configurabile)
- **API ZCS**: Una thingKey per richiesta
- **RAM**: Minimo 8GB disponibili
- **Porte richieste**: 80, 3000, 5432, 5678, 6379, 8000, 8086, 1883, 9001

### Operativi
- Autenticazione API ZCS con header `Authorization: Zcs [token]`
- Parametro `client` obbligatorio in ogni richiesta
- Endpoint POST: `https://third.zcsazzurroportal.com:19003/`

---

## 4. Decisioni Architetturali

### Backend
| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Framework | FastAPI | Async native, performance |
| ORM | SQLAlchemy 2.0 | Async support, maturo |
| Task Queue | Celery + Redis | Scheduling avanzato |
| Cache | Redis + Memory (cachetools) | Multi-layer, resiliente |
| Time Series | InfluxDB | Ottimizzato per metriche |

### Auth Service
| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Servizio | FastAPI dedicato | Validazione centralizzata |
| Porta | 8001 | Separato da backend |
| JWT | python-jose | Validazione RS256 |

### Frontend
| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Framework | RefineJS + React | Admin dashboard ready |
| UI Library | Ant Design | Enterprise-grade |
| Auth | Auth0 | SSO, sicuro |
| State | React Query | Cache + sync |

### Infrastruttura
| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Container | Docker Compose | Dev/prod parity |
| Proxy | Nginx | SSL termination |
| MQTT | Mosquitto | Lightweight, IoT standard |
| Automation | N8N | Visual workflows |

---

## 5. Architettura

```
┌──────────────────────────────────────────────────────────────────────┐
│                           NGINX (80/443)                             │
└──────────────────────────────────────────────────────────────────────┘
         │                          │                    │
         ▼                          ▼                    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │   Backend API   │    │      N8N        │
│   (RefineJS)    │    │   (FastAPI)     │    │  (Automations)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5678    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                    │ │ │ │
         │                    │ │ │ └───────────────┐
         │         ┌──────────┘ │ └──────────┐      │
         │         ▼            ▼            ▼      ▼
         │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
         │  │PostgreSQL │ │ InfluxDB  │ │   Redis   │ │Auth Service│
         │  │  (5432)   │ │  (8086)   │ │  (6379)   │ │  (8001)   │
         │  └───────────┘ └───────────┘ └───────────┘ └───────────┘
         │                      ▲                          │
         │         ┌────────────┴────────────┐             ▼
         │         │                         │      ┌───────────┐
         │  ┌─────────────┐          ┌─────────────┐│   Auth0   │
         │  │Celery Worker│          │ Celery Beat ││   (SSO)   │
         │  │  (2 tasks)  │          │ (Scheduler) │└───────────┘
         │  └─────────────┘          └─────────────┘
         │              │
         │              ▼
         │  ┌─────────────────────────────────┐
         │  │        ZCS API External         │
         │  │   third.zcsazzurroportal.com    │
         │  └─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    Mosquitto    │ (non usato attualmente)
│   MQTT (1883)   │
└─────────────────┘
```

---

## 6. Stack Tecnologico

### Backend (Python 3.11+)
```
fastapi==0.104.1          # Web framework
sqlalchemy==2.0.23        # ORM
asyncpg==0.29.0           # PostgreSQL async
influxdb-client==1.39.0   # Time series
redis==4.6.0              # Cache
celery==5.3.4             # Task queue
celery-redbeat==2.3.2     # Redis scheduler
httpx==0.25.2             # HTTP client
pydantic==2.5.0           # Validation
structlog==23.2.0         # Logging
```

### Frontend (Node 18+)
```
@refinedev/core: ^4.45.0
@refinedev/antd: ^5.35.0
@auth0/auth0-react: ^2.2.0
@ant-design/charts: ^1.4.2
antd: ^5.8.0
react: ^18.2.0
axios: ^1.4.0
```

---

## 7. API ZCS Azzurro Portal

### Endpoint Base
```
POST https://third.zcsazzurroportal.com:19003/
Headers:
  - Authorization: Zcs [AUTH_TOKEN]
  - client: [CLIENT_CODE]
  - Content-Type: application/json
```

### Metodi Disponibili

#### 7.1 realtimeData
Dati tempo reale per dispositivi.

**Request:**
```json
{
  "realtimeData": {
    "command": "realtimeData",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*"
    }
  }
}
```

**Required Values:**
- lastUpdate, thingFind
- batteryCycletime, batterySoC
- powerCharging, powerDischarging, powerExporting, powerImporting
- powerConsuming, powerAutoconsuming, powerGenerating, powerGeneratingExt
- energyCharging, energyDischarging, energyExporting, energyImporting
- energyConsuming, energyAutoconsuming, energyGenerating
- energyChargingTotal, energyDischargingTotal, energyExportingTotal
- energyImportingTotal, energyConsumingTotal, energyAutoconsumingTotal
- energyGeneratingTotal
- `*` = tutti

#### 7.2 historicData
Dati storici (max 24h per richiesta).

**Request:**
```json
{
  "historicData": {
    "command": "historicData",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*",
      "start": "2021-09-15T00:00:00.000Z",
      "end": "2021-09-15T23:59:59.059Z"
    }
  }
}
```

**Additional Required Values:**
- currentAC, voltageAC, powerDC, currentDC, voltageDC
- frequency, temperature
- *Decimal variants per energy totals

#### 7.3 deviceAlarm
Stato allarmi corrente.

**Request:**
```json
{
  "deviceAlarm": {
    "command": "deviceAlarm",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*"
    }
  }
}
```

**Response:** Array di codici allarme attivi + lastUpdate

#### 7.4 deviceHistoricAlarm
Storico allarmi (max 24h per richiesta).

**Request:**
```json
{
  "deviceHistoricAlarm": {
    "command": "deviceHistoricAlarm",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*",
      "start": "2021-09-15T00:00:00.000Z",
      "end": "2021-09-15T23:59:59.059Z"
    }
  }
}
```

---

## 8. Modello Dati

### PostgreSQL Schema

```sql
-- Tabelle principali
users (id, auth0_id, email, name, picture, created_at, last_login)
user_permissions (id, user_id, permission, resource, granted_at)
devices (id, thing_key, name, type, location, manufacturer, model, firmware_version)
device_configurations (id, device_id, config_key, config_value, data_type)
notification_channels (id, name, type, config, enabled)
alert_rules (id, name, device_id, condition_type, condition_config, severity)
notifications_log (id, alert_rule_id, channel_id, message, status, sent_at)
audit_log (id, user_id, action, resource_type, resource_id, details, timestamp)
```

### InfluxDB Measurements

| Measurement | Tags | Fields |
|-------------|------|--------|
| power_data | device_key, device_type | power_*, voltage, current, frequency, temperature |
| energy_data | device_key, device_type | energy_total, energy_daily, energy_monthly, energy_* |
| battery_data | device_key, device_type | soc, voltage, current, temperature, cycle_count, health |
| alarm_data | device_key, device_type, alarm_code, severity | is_active, alarm_numeric_code |

---

## 9. API Backend Endpoints

### Health
```
GET  /api/v1/health/           # Health check base
GET  /api/v1/health/detailed   # Status dettagliato
GET  /api/v1/health/database   # Connettività DB
GET  /api/v1/health/external   # Servizi esterni
```

### Devices
```
GET  /api/v1/devices/          # Lista dispositivi
GET  /api/v1/devices/{id}      # Dettaglio singolo
GET  /api/v1/devices/{id}/realtime  # Dati realtime
GET  /api/v1/devices/{id}/historic  # Dati storici
```

### Data
```
GET  /api/v1/data/realtime     # Aggregato sistema
GET  /api/v1/data/historical   # Storico aggregato
GET  /api/v1/data/summary      # Summary sistema
GET  /api/v1/data/monitoring   # Stato raccolta
POST /api/v1/data/collection/trigger  # Trigger manuale
GET  /api/v1/data/collection/status   # Status collection
```

### Alarms
```
GET  /api/v1/alarms/           # Allarmi sistema
GET  /api/v1/alarms/device/{id}  # Allarmi dispositivo
GET  /api/v1/alarms/historic   # Storico
GET  /api/v1/alarms/summary    # Summary attivi
POST /api/v1/alarms/{id}/acknowledge  # Acknowledge
```

### Tasks
```
GET  /api/v1/tasks/status      # Status sistema
GET  /api/v1/tasks/active      # Task attivi
GET  /api/v1/tasks/scheduled   # Schedulati
GET  /api/v1/tasks/history     # Storico
GET  /api/v1/tasks/{id}        # Dettaglio task
POST /api/v1/tasks/trigger/{name}  # Trigger manuale
DELETE /api/v1/tasks/{id}      # Revoke task
GET  /api/v1/tasks/workers/stats  # Stats worker
```

---

## 10. Task Scheduling Celery

| Task | Schedule | Descrizione |
|------|----------|-------------|
| collect_realtime_data | ogni 2 min | Raccolta dati tempo reale |
| collect_alarm_data | ogni 30 sec | Raccolta stato allarmi |
| health_check_task | ogni 5 min | Health check sistema |

---

## 11. Configurazione Cache

### TTL per Tipo Dato
| DataType | TTL Default | TTL Ore Picco (10-16) |
|----------|-------------|----------------------|
| REALTIME | 60s | 30s |
| HISTORIC | 3600s | 3600s |
| ALARMS | 30s | 30s |
| TOTALS | 300s | 300s |
| DEVICE_INFO | 1800s | 1800s |
| AGGREGATED | 900s | 900s |

---

## 12. Variabili Ambiente Richieste

```bash
# Database
POSTGRES_DB=sunpulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[REQUIRED]

# InfluxDB
INFLUXDB_DB=solar_metrics
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=[REQUIRED]
INFLUXDB_USER=solar_user
INFLUXDB_USER_PASSWORD=[REQUIRED]

# Redis
REDIS_PASSWORD=[REQUIRED]

# ZCS API
ZCS_API_URL=https://third.zcsazzurroportal.com:19003/
ZCS_API_AUTH=Zcs [TOKEN]
ZCS_CLIENT_CODE=[CLIENT_CODE]
ZCS_DEVICE_KEYS=ZE1ES330J9E558  # comma-separated

# Auth0
AUTH0_DOMAIN=[DOMAIN].eu.auth0.com
AUTH0_CLIENT_ID=[CLIENT_ID]
AUTH0_CLIENT_SECRET=[SECRET]

# App
SECRET_KEY=[GENERATED]
DEBUG=False
ENVIRONMENT=production
```

---

## 13. Performance Target

### API Response Times
| Endpoint Type | Target |
|---------------|--------|
| Health checks | < 100ms |
| Device data (cached) | < 500ms |
| System aggregations | < 1s |
| Historic queries | < 2s |

### Cache Performance
- Target hit rate: > 80%

### Task Execution
| Task | Durata media |
|------|--------------|
| Realtime collection | ~30s |
| Alarm collection | ~15s |
| Health checks | ~10s |

---

## 14. Dispositivi Configurati

**Dispositivo corrente:**
- `ZE1ES330J9E558` - Inverter ZCS (default configurato)

---

## 15. Rischi Aperti

| ID | Rischio | Impatto | Probabilità | Mitigazione |
|----|---------|---------|-------------|-------------|
| R1 | Rate limiting API ZCS non documentato | Alto | Media | Circuit breaker implementato, monitoring chiamate |
| R2 | Downtime API ZCS | Alto | Bassa | Cache fallback, retry con backoff |
| R3 | Volumi dati storici elevati | Medio | Media | Chunking 24h implementato |
| R4 | Mancanza documentazione codici allarme | Medio | Alta | Mapping da inverter, contattare ZCS |
| R5 | Auth0 token expiration | Medio | Bassa | Refresh token implementato |

---

## 16. Prossime Azioni

> ⚠️ **IMPORTANTE**: Tutti i bug, miglioramenti e task sono tracciati in **[TODO.md](../TODO.md)**
> 
> Il file TODO.md contiene:
> - 🔴 Bug critici da fixare (7)
> - ⚠️ Problemi architetturali (6)
> - 🟡 Miglioramenti UX/UI (11)
> - 🟢 Nice-to-have (8)
> - 📋 Pagine da completare (4)
> - 🔧 Task infrastruttura (6)

### Quick Reference Priorità

| Priorità | Descrizione |
|----------|-------------|
| 🔴 Critico | Fix immediati - bug che bloccano funzionalità |
| ⚠️ Alto | Problemi architetturali - da risolvere prima di produzione |
| 🟡 Medio | UX/UI improvements - migliorano esperienza utente |
| 🟢 Basso | Nice-to-have - quando c'è tempo |

---

## 17. Cronologia

| Data | Evento |
|------|--------|
| 2024-Q4 | Inizio progetto, setup infrastruttura |
| 2024-Q4 | Fase 1 completata: core MVP |
| 2024-Q4 | Fase 2 completata: integrazione ZCS |
| 2025-12 | Fase 3 in corso: frontend dashboard |

---

## 18. Gap da Colmare

> 📋 **Vedi [TODO.md](../TODO.md)** per lista completa e dettagliata di tutti i task

### Documentazione Mancante
- [ ] Mappatura completa codici allarme ZCS → descrizioni
- [ ] Limiti rate API ZCS (attuale: stima 100/h)
- [ ] Documentazione dettagliata modelli inverter supportati
- [ ] Schema dati dettagliato risposta ZCS per ogni tipo device

### Bug e Fix Necessari
- Vedi sezione **🔴 BUG CRITICI** in [TODO.md](../TODO.md)
- 7 bug critici identificati (backend + frontend)
- 6 problemi architetturali da risolvere

### UX/UI da Migliorare
- Vedi sezione **🟡 UX/UI IMPROVEMENTS** in [TODO.md](../TODO.md)
- 11 miglioramenti identificati

---

## 19. Riferimenti Esterni

- **ZCS Azzurro Portal Documentation**: https://www.zcsazzurro.com/it/documentazione
- **ZCS API Spec**: `doc/Specifica API 1.8 del 10-03-2025 (IT)/input.md`
- **Manuale Inverter**: `doc/Manuale-Inveter-3000SP-IT_2023-12-227-164047_rkjo.md`
- **Auth0 Dashboard**: https://manage.auth0.com
- **RefineJS Docs**: https://refine.dev/docs
- **Ant Design**: https://ant.design/components

---

## 20. Comandi Utili

### Avvio Sistema
```bash
# Setup iniziale
./scripts/setup.sh

# Avvio servizi
docker-compose up -d

# Logs
docker-compose logs -f backend celery-worker celery-beat
```

### Test
```bash
# Test integrazione Fase 2
python test_phase2_integration.py

# Test API manuale
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/devices/
```

### Database
```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d sunpulse

# Redis
docker-compose exec redis redis-cli

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

### Celery
```bash
# Restart worker
docker-compose restart celery-worker celery-beat

# Flower monitoring
open http://localhost:5555
```

---

*Questo file viene rigenerato automaticamente. Non modificare manualmente.*


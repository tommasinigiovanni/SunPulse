<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.11+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/node-18+-green.svg" alt="Node">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
</p>

# ☀️ SunPulse

**Piattaforma di monitoraggio per impianti fotovoltaici con integrazione ZCS Azzurro Portal**

SunPulse è una dashboard completa per il monitoraggio real-time di impianti fotovoltaici. Integra le API ZCS Azzurro per raccogliere dati di produzione, consumo, batterie e allarmi.

---

## ✨ Features

- 📊 **Dashboard Real-time** - Visualizzazione dati in tempo reale
- 📈 **Analisi Storiche** - Grafici produzione/consumo con aggregazioni
- 🔔 **Gestione Allarmi** - Monitoraggio e notifiche allarmi dispositivi
- 🔋 **Stato Batterie** - Monitoraggio SOC e cicli batteria
- ⚡ **Cache Intelligente** - Multi-layer caching (Memory + Redis)
- 🛡️ **Resilienza** - Circuit breaker per fault tolerance
- 🔐 **Autenticazione** - Auth0 integration
- 🐳 **Docker Ready** - Deploy con un comando

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────┐
│                      NGINX (80/443)                     │
└─────────────────────────────────────────────────────────┘
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ Frontend │   │ Backend  │   │   N8N    │
       │ (React)  │   │(FastAPI) │   │(Workflow)│
       │  :3000   │   │  :8000   │   │  :5678   │
       └──────────┘   └──────────┘   └──────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │PostgreSQL│       │ InfluxDB │       │  Redis   │
   │  :5432   │       │  :8086   │       │  :6379   │
   └──────────┘       └──────────┘       └──────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
            ┌──────────┐        ┌──────────┐
            │  Celery  │        │  Celery  │
            │  Worker  │        │   Beat   │
            └──────────┘        └──────────┘
                  │
                  ▼
         ┌────────────────┐
         │  ZCS Azzurro   │
         │     API        │
         └────────────────┘
```

---

## 🚀 Quick Start

### Prerequisiti

- Docker & Docker Compose
- 8GB RAM disponibili
- Credenziali API ZCS Azzurro

### Installazione

```bash
# 1. Clona il repository
git clone https://github.com/yourusername/sunpulse.git
cd sunpulse

# 2. Copia e configura le variabili d'ambiente
cp .env.example .env
# Modifica .env con le tue credenziali

# 3. Avvia tutti i servizi
docker-compose up -d

# 4. Verifica lo stato
docker-compose ps
```

### Accesso

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| Frontend | http://localhost:3000 | Dashboard principale |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| N8N | http://localhost:5678 | Automazioni |

---

## ⚙️ Configurazione

### Variabili d'Ambiente

```bash
# ZCS API (obbligatorio)
ZCS_API_URL=https://third.zcsazzurroportal.com:19003/
ZCS_API_AUTH=Zcs YOUR_TOKEN
ZCS_CLIENT_CODE=YOUR_CLIENT_CODE
ZCS_DEVICE_KEYS=YOUR_DEVICE_KEY

# Auth0
AUTH0_DOMAIN=your-domain.eu.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret

# Database
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password
INFLUXDB_ADMIN_PASSWORD=your_secure_password
```

### Ottenere Credenziali ZCS

1. Contatta [ZCS Azzurro](https://www.zcsazzurro.com/it/documentazione) per richiedere accesso API
2. Riceverai: `client code` e `authorization token`
3. Identifica le `thingKey` dei tuoi dispositivi

---

## 📁 Struttura Progetto

```
sunpulse/
├── docker-compose.yml      # Orchestrazione servizi
├── .env.example            # Template variabili ambiente
├── README.md               # Documentazione
├── TODO.md                 # Task e roadmap
├── LICENSE                 # Licenza MIT
├── doc/                    # Documentazione tecnica
│   ├── context.md          # Knowledge base progetto
│   └── *.pdf               # Specifiche ZCS
├── modules/
│   ├── backend/            # FastAPI application
│   │   ├── app/
│   │   │   ├── api/        # REST endpoints
│   │   │   ├── config/     # Configurazione
│   │   │   ├── models/     # Data models
│   │   │   ├── services/   # Business logic
│   │   │   └── utils/      # Utilities
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── frontend/           # React/Refine application
│   │   ├── src/
│   │   │   ├── components/ # UI components
│   │   │   ├── hooks/      # React hooks
│   │   │   ├── pages/      # Page components
│   │   │   └── utils/      # Utilities
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── auth/               # Auth service
│   ├── postgres/           # Database init
│   ├── influxdb/           # Time-series DB
│   ├── redis/              # Cache
│   ├── n8n/                # Automations
│   └── nginx/              # Reverse proxy
└── scripts/                # Utility scripts
```

---

## 🔌 API Endpoints

### Health
```
GET  /api/v1/health/           # Health check
GET  /api/v1/health/detailed   # Status dettagliato
```

### Devices
```
GET  /api/v1/devices/          # Lista dispositivi
GET  /api/v1/devices/{id}      # Dettaglio dispositivo
GET  /api/v1/devices/{id}/realtime   # Dati real-time
GET  /api/v1/devices/{id}/historic   # Dati storici
```

### Data
```
GET  /api/v1/data/realtime     # Dati aggregati real-time
GET  /api/v1/data/historical   # Dati storici sistema
GET  /api/v1/data/summary      # Summary giornaliero
```

### Alarms
```
GET  /api/v1/alarms/           # Lista allarmi
GET  /api/v1/alarms/summary    # Summary allarmi attivi
```

---

## 🛠️ Stack Tecnologico

### Backend
- **FastAPI** - Web framework async
- **PostgreSQL** - Database relazionale
- **InfluxDB** - Database time-series
- **Redis** - Cache e message broker
- **Celery** - Task queue e scheduling

### Frontend
- **React 18** - UI library
- **Refine** - Admin framework
- **Ant Design** - Component library
- **Auth0** - Authentication

### Infrastructure
- **Docker** - Containerizzazione
- **Nginx** - Reverse proxy
- **N8N** - Workflow automation

---

## 📊 Task Scheduling

| Task | Frequenza | Descrizione |
|------|-----------|-------------|
| `collect_realtime_data` | 2 min | Raccolta dati produzione |
| `collect_alarm_data` | 30 sec | Verifica allarmi |
| `health_check_task` | 5 min | Health check sistema |

---

## 🧪 Development

```bash
# Avvia in modalità development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Logs in tempo reale
docker-compose logs -f backend

# Ricostruisci dopo modifiche
docker-compose build backend
docker-compose up -d backend

# Test
cd modules/backend && pytest
cd modules/frontend && npm test
```

---

## 📖 Documentazione

- [Context File](doc/context.md) - Knowledge base completa del progetto
- [TODO](TODO.md) - Task, bug e roadmap
- [API ZCS](doc/) - Specifiche API ZCS Azzurro

---

## 🤝 Contributing

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

---

## 📄 License

Distribuito sotto licenza MIT. Vedi [LICENSE](LICENSE) per maggiori informazioni.

---

## 🙏 Acknowledgments

- [ZCS Azzurro](https://www.zcsazzurro.com) - API e documentazione
- [Refine](https://refine.dev) - Admin framework
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework

---

<p align="center">
  <strong>☀️ SunPulse - Monitora la tua energia solare</strong>
</p>

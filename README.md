<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.11+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/node-18+-green.svg" alt="Node">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
</p>

# ☀️ SunPulse

**Solar photovoltaic monitoring platform with ZCS Azzurro Portal integration**

SunPulse is a comprehensive dashboard for real-time monitoring of solar PV systems. It integrates with ZCS Azzurro APIs to collect production, consumption, battery and alarm data.

---

## ✨ Features

- 📊 **Real-time Dashboard** - Live data visualization
- 📈 **Historical Analysis** - Production/consumption charts with aggregations
- 🔔 **Alarm Management** - Device alarm monitoring and notifications
- 🔋 **Battery Status** - SOC and battery cycle monitoring
- ⚡ **Smart Caching** - Multi-layer caching (Memory + Redis)
- 🛡️ **Resilience** - Circuit breaker for fault tolerance
- 🔐 **Authentication** - Auth0 integration
- 🐳 **Docker Ready** - Deploy with a single command

---

## 🏗️ Architecture

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

### Prerequisites

- Docker & Docker Compose
- 8GB available RAM
- ZCS Azzurro API credentials

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/tommasinigiovanni/SunPulse.git
cd sunpulse

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps
```

### Access

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main dashboard |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| N8N | http://localhost:5678 | Automations |

---

## ⚙️ Configuration

### Environment Variables

```bash
# ZCS API (required)
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

### Getting ZCS Credentials

1. Contact [ZCS Azzurro](https://www.zcsazzurro.com/it/documentazione) to request API access
2. You will receive: `client code` and `authorization token`
3. Identify your devices' `thingKey`

---

## 📁 Project Structure

```
sunpulse/
├── docker-compose.yml      # Service orchestration
├── .env.example            # Environment template
├── README.md               # Documentation
├── TODO.md                 # Tasks and roadmap
├── LICENSE                 # MIT License
├── doc/                    # Technical documentation
│   ├── context.md          # Project knowledge base
│   └── *.pdf               # ZCS specifications
├── modules/
│   ├── backend/            # FastAPI application
│   │   ├── app/
│   │   │   ├── api/        # REST endpoints
│   │   │   ├── config/     # Configuration
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
GET  /api/v1/health/detailed   # Detailed status
```

### Devices
```
GET  /api/v1/devices/          # List devices
GET  /api/v1/devices/{id}      # Device details
GET  /api/v1/devices/{id}/realtime   # Real-time data
GET  /api/v1/devices/{id}/historic   # Historical data
```

### Data
```
GET  /api/v1/data/realtime     # Aggregated real-time data
GET  /api/v1/data/historical   # System historical data
GET  /api/v1/data/summary      # Daily summary
```

### Alarms
```
GET  /api/v1/alarms/           # List alarms
GET  /api/v1/alarms/summary    # Active alarms summary
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async web framework
- **PostgreSQL** - Relational database
- **InfluxDB** - Time-series database
- **Redis** - Cache and message broker
- **Celery** - Task queue and scheduling

### Frontend
- **React 18** - UI library
- **Refine** - Admin framework
- **Ant Design** - Component library
- **Auth0** - Authentication

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **N8N** - Workflow automation

---

## 📊 Task Scheduling

| Task | Frequency | Description |
|------|-----------|-------------|
| `collect_realtime_data` | 2 min | Production data collection |
| `collect_alarm_data` | 30 sec | Alarm status check |
| `health_check_task` | 5 min | System health check |

---

## 🧪 Development

```bash
# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Real-time logs
docker-compose logs -f backend

# Rebuild after changes
docker-compose build backend
docker-compose up -d backend

# Tests
cd modules/backend && pytest
cd modules/frontend && npm test
```

---

## 📖 Documentation

- [Context File](doc/context.md) - Complete project knowledge base
- [TODO](TODO.md) - Tasks, bugs and roadmap
- [ZCS API](doc/) - ZCS Azzurro API specifications

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under MIT License. See [LICENSE](LICENSE) for more information.

---

## 🙏 Acknowledgments

- [ZCS Azzurro](https://www.zcsazzurro.com) - API and documentation
- [Refine](https://refine.dev) - Admin framework
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework

---

<p align="center">
  <strong>☀️ SunPulse - Monitor your solar energy</strong>
</p>

# 🚀 Deploy in Produzione con HTTPS

## Prerequisiti

1. **Dominio**: `sunpulse.giovannitommasini.it` puntato all'IP della VM
2. **Porte aperte**: 80 e 443 (per Let's Encrypt e HTTPS)
3. **Docker e Docker Compose** installati sulla VM

## Setup Rapido

### 1. Clona il repository sulla VM

```bash
git clone https://github.com/yourusername/sunpulse.git
cd sunpulse
```

### 2. Crea il file `.env.prod`

```bash
# Copia il template
cp .env .env.prod

# Modifica con i valori di produzione
nano .env.prod
```

### 3. Variabili da configurare in `.env.prod`

```env
# Dominio principale
DOMAIN=sunpulse.giovannitommasini.it

# Email per Let's Encrypt
ACME_EMAIL=tommasini.giovanni@gmail.com

# Traefik Dashboard (genera con: htpasswd -nb admin tuapassword)
# NOTA: I $ devono essere raddoppiati (es: $apr1$ diventa $$apr1$$)
TRAEFIK_DASHBOARD_AUTH=admin:$$apr1$$xyz...

# URL Frontend per HTTPS
VITE_API_URL=https://sunpulse.giovannitommasini.it/api/v1
VITE_WS_URL=wss://sunpulse.giovannitommasini.it/ws

# Disabilita modalità sviluppo
VITE_AUTH_DEV_MODE=false
DEBUG=False
ENVIRONMENT=production

# Password sicure (genera con: openssl rand -base64 32)
POSTGRES_PASSWORD=<password-forte>
REDIS_PASSWORD=<password-forte>
SECRET_KEY=<chiave-lunga-random>
```

### 4. Configura Auth0

Nel [Dashboard Auth0](https://manage.auth0.com/), configura la tua applicazione:

- **Allowed Callback URLs**: `https://sunpulse.giovannitommasini.it`
- **Allowed Logout URLs**: `https://sunpulse.giovannitommasini.it`  
- **Allowed Web Origins**: `https://sunpulse.giovannitommasini.it`

### 5. Build e Deploy

```bash
# Build con le variabili di produzione
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml build

# Avvia i servizi
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 6. Verifica

```bash
# Controlla i container
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Logs di Traefik (per debug certificati)
docker logs sunpulse_traefik -f

# Test HTTPS
curl -I https://sunpulse.giovannitommasini.it
```

## Architettura in Produzione

```
                    Internet
                        │
                        ▼
                   ┌─────────┐
                   │ Traefik │ (:80, :443)
                   │  + SSL  │
                   └────┬────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │Frontend │    │ Backend │    │   N8N   │
   │  React  │    │ FastAPI │    │         │
   └─────────┘    └─────────┘    └─────────┘
        │               │
        └───────┬───────┘
                │
   ┌────────────┼────────────┐
   │            │            │
   ▼            ▼            ▼
┌──────┐   ┌─────────┐   ┌───────┐
│Postgres│  │InfluxDB │   │ Redis │
└──────┘   └─────────┘   └───────┘
```

## Domini Disponibili

| Servizio | URL |
|----------|-----|
| Frontend | `https://sunpulse.giovannitommasini.it` |
| API | `https://sunpulse.giovannitommasini.it/api/v1` |
| N8N | `https://n8n.sunpulse.giovannitommasini.it` |
| Traefik Dashboard | `https://traefik.sunpulse.giovannitommasini.it` |

## Comandi Utili

```bash
# Riavvia un servizio
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart frontend

# Rebuild frontend (dopo modifiche)
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend

# Logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f frontend backend

# Stop tutto
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

## Troubleshooting

### Certificato non generato

1. Verifica che il dominio punti alla VM:
   ```bash
   dig sunpulse.giovannitommasini.it
   ```

2. Verifica che le porte 80/443 siano aperte:
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   ```

3. Controlla i log di Traefik:
   ```bash
   docker logs sunpulse_traefik | grep -i acme
   ```

### Auth0 "Secure Origin" Error

Verifica che:
- `VITE_AUTH_DEV_MODE=false` in `.env.prod`
- Il frontend sia stato rebuilded con `docker compose build frontend`
- Stai accedendo via HTTPS

### Backend non raggiungibile

```bash
# Test diretto al container
docker exec sunpulse_traefik wget -qO- http://backend:8000/api/v1/health/ping
```

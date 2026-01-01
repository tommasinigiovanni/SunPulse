# Sistema Audit Log - SunPulse

Sistema completo di audit logging per tracciare tutte le azioni degli utenti e le chiamate API.

## Caratteristiche

### Backend

#### 1. Modello Database (`app/models/audit.py`)

Tabella `audit_logs` con i seguenti campi:

- **User Information**: `user_id`, `user_email`, `user_name`
- **Action Details**: `action`, `action_category`, `resource_type`, `resource_id`
- **Request Details**: `method`, `endpoint`, `ip_address`, `user_agent`
- **Response Details**: `status_code`, `success`, `error_message`, `duration_ms`
- **Data Context**: `request_data`, `response_data`, `metadata`
- **Timing**: `timestamp`
- **Session Tracking**: `session_id`

**Indici ottimizzati** per query veloci:
- `idx_audit_user_timestamp`: ricerche per utente e periodo
- `idx_audit_action_timestamp`: ricerche per azione e periodo
- `idx_audit_resource`: ricerche per risorsa
- `idx_audit_timestamp_action`: ordinamento temporale

#### 2. Middleware Automatico (`app/middleware/audit_middleware.py`)

**Caratteristiche:**
- Logging automatico di tutte le richieste API
- Cattura informazioni utente da headers/auth
- Sanitizzazione dati sensibili (password, token, API keys)
- Calcolo durata richieste
- Gestione errori non bloccante
- Path esclusi configurabili (health checks, docs, ecc.)

**Configurazione:**
```python
app.add_middleware(
    AuditMiddleware,
    audit_service=audit_service,
    exclude_paths=["/health", "/docs", "/openapi.json"],
    log_request_body=True,
    log_response_body=False,
    max_body_length=10000,
)
```

#### 3. Audit Service (`app/services/audit_service.py`)

**Funzionalità:**

- `create_log()`: Crea entry di audit log
- `get_logs()`: Query con filtri avanzati e paginazione
- `get_log_by_id()`: Recupera singolo log
- `get_stats()`: Statistiche aggregate
- `cleanup_old_logs()`: Retention policy (90 giorni default)
- `export_logs()`: Export JSON/CSV
- `get_user_activity()`: Attività utente specifico
- `get_resource_history()`: Storico risorsa specifica

**Retention Policy:**
- Default: 90 giorni
- Cleanup automatico configurabile
- Endpoint manuale per cleanup: `POST /api/v1/audit/cleanup`

#### 4. API Endpoints (`app/api/v1/audit.py`)

##### GET `/api/v1/audit/`
Lista audit logs con filtri avanzati

**Query Parameters:**
- `user_id`: Filtra per user ID
- `user_email`: Filtra per email (like)
- `action`: Filtra per tipo azione
- `action_category`: Filtra per categoria
- `resource_type`: Filtra per tipo risorsa
- `resource_id`: Filtra per ID risorsa
- `ip_address`: Filtra per IP
- `success`: Filtra per esito (success/failure/error)
- `date_from`: Data inizio periodo
- `date_to`: Data fine periodo
- `limit`: Numero risultati (1-1000)
- `offset`: Offset paginazione
- `sort_by`: Campo ordinamento
- `sort_order`: Ordine (asc/desc)

**Response:**
```json
{
  "logs": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

##### GET `/api/v1/audit/{log_id}`
Dettaglio singolo audit log

##### GET `/api/v1/audit/stats/summary`
Statistiche aggregate

**Query Parameters:**
- `date_from`: Data inizio periodo
- `date_to`: Data fine periodo

**Response:**
```json
{
  "total_logs": 1523,
  "unique_users": 12,
  "actions_by_type": {
    "device_view": 450,
    "alarm_view": 230,
    "data_export": 15
  },
  "actions_by_category": {
    "device": 450,
    "alarm": 230,
    "data": 15
  },
  "success_rate": 98.5,
  "period_start": "2025-01-01T00:00:00Z",
  "period_end": "2025-01-31T23:59:59Z"
}
```

##### GET `/api/v1/audit/user/{user_id}/activity`
Attività recente di un utente (max 500 risultati)

##### GET `/api/v1/audit/resource/{resource_type}/{resource_id}/history`
Storico azioni su una risorsa (max 200 risultati)

##### GET `/api/v1/audit/export/csv`
Export CSV (max 10.000 record)

**Include campi base:**
- id, timestamp, user_email, user_name
- action, action_category, resource_type, resource_id
- method, endpoint, ip_address
- status_code, success, duration_ms, error_message

##### GET `/api/v1/audit/export/json`
Export JSON completo (max 10.000 record)

**Include tutti i dettagli:**
- Tutti i campi base
- request_data, response_data, metadata
- user_agent completo

**Response:**
```json
{
  "export_date": "2025-01-15T12:30:00Z",
  "total_records": 150,
  "filters": {
    "user_id": "...",
    "date_from": "...",
    "date_to": "..."
  },
  "logs": [...]
}
```

##### POST `/api/v1/audit/cleanup`
Cleanup manuale dei log vecchi

**Query Parameters:**
- `retention_days`: Giorni di retention (default: 90)

**Response:**
```json
{
  "status": "success",
  "deleted_count": 523,
  "retention_days": 90
}
```

### Frontend

#### Pagina Audit (`/admin/audit`)

**Componenti:**

1. **Statistics Cards**
   - Totale log
   - Utenti unici
   - Success rate
   - Categorie attive

2. **Filtri Avanzati**
   - Email utente (ricerca)
   - Azione (input)
   - Categoria (select)
   - Esito (select: success/failure/error)
   - Periodo (date range picker con orario)
   - Pulsanti Cerca e Reset

3. **Tabella Log**
   - Colonne: Timestamp, Utente, Azione, Categoria, Risorsa, Endpoint, IP, Status, Durata
   - Ordinamento per timestamp (desc default)
   - Paginazione (10/25/50/100 per pagina)
   - Azione "Visualizza dettaglio" per ogni riga

4. **Modal Dettaglio**
   - Tutte le informazioni complete del log
   - Request/Response data in formato JSON
   - Metadata aggiuntivi
   - User agent completo

5. **Export**
   - Pulsante "Export CSV"
   - Pulsante "Export JSON"
   - Rispetta i filtri applicati
   - Download automatico file

**Tecnologie:**
- React + TypeScript
- Ant Design components
- Axios per API calls
- dayjs per date formatting

## Tipi di Azioni Tracciate

### Authentication
- `login`: Accesso utente
- `logout`: Uscita utente
- `login_failed`: Tentativo fallito

### Device Operations
- `device_create`: Creazione dispositivo
- `device_update`: Aggiornamento dispositivo
- `device_delete`: Eliminazione dispositivo
- `device_view`: Visualizzazione dispositivo

### Configuration
- `config_update`: Aggiornamento configurazione
- `config_view`: Visualizzazione configurazione

### Alarms
- `alarm_acknowledge`: Riconoscimento allarme
- `alarm_resolve`: Risoluzione allarme
- `alarm_view`: Visualizzazione allarmi

### Data Access
- `data_export`: Export dati
- `data_view`: Visualizzazione dati
- `report_generate`: Generazione report

### Settings
- `settings_update`: Aggiornamento impostazioni
- `settings_view`: Visualizzazione impostazioni

### User Management
- `user_create`: Creazione utente
- `user_update`: Aggiornamento utente
- `user_delete`: Eliminazione utente
- `user_view`: Visualizzazione utente

### API Access
- `api_access`: Accesso API generico
- `api_error`: Errore API

### System
- `system_error`: Errore di sistema
- `system_start`: Avvio sistema
- `system_stop`: Arresto sistema

## Categorie Azioni

- `auth`: Autenticazione/autorizzazione
- `device`: Operazioni su dispositivi
- `alarm`: Gestione allarmi
- `data`: Accesso/export dati
- `settings`: Configurazione sistema
- `api`: Chiamate API generiche
- `audit`: Accesso ai log di audit
- `user`: Gestione utenti

## Sicurezza e Privacy

### Sanitizzazione Dati
Il middleware rimuove automaticamente dati sensibili da request_data:
- password
- token
- secret
- api_key
- authorization
- credential
- private_key

I valori sensibili vengono sostituiti con `***REDACTED***`.

### Limitazioni Export
- CSV: max 10.000 record, solo campi base
- JSON: max 10.000 record, dati completi
- Timeout: 60 secondi per export

### Accesso
- L'endpoint `/api/v1/audit/` richiede autenticazione
- La pagina `/admin/audit` richiede ruolo admin (da implementare in produzione)
- I log contengono informazioni sensibili: proteggere adeguatamente

## Performance

### Indici Database
Gli indici compositi ottimizzano le query più comuni:
- Ricerca per utente e periodo
- Ricerca per azione e periodo
- Ricerca per risorsa
- Ordinamento temporale

### Middleware
- Logging asincrono non bloccante
- Errori nel logging non bloccano richieste
- Cache delle sessioni utente
- Limitazione dimensione body loggato

### Query
- Paginazione efficiente con offset/limit
- Filtri applicati a livello database
- Count ottimizzato con indici
- Statistiche pre-aggregate dove possibile

## Configurazione

### Backend

**Environment Variables:**
```bash
# Database (già esistente)
DATABASE_URL=postgresql://user:pass@localhost/sunpulse

# Audit Settings (opzionali)
AUDIT_RETENTION_DAYS=90
AUDIT_CLEANUP_ENABLED=true
AUDIT_LOG_REQUEST_BODY=true
AUDIT_LOG_RESPONSE_BODY=false
AUDIT_MAX_BODY_LENGTH=10000
```

### Attivazione

Il middleware è già attivato in `app/main.py`. Per disabilitarlo temporaneamente, commentare:

```python
# app.add_middleware(AuditMiddleware, ...)
```

### Cleanup Automatico

Per abilitare cleanup automatico schedulato, configurare un task Celery:

```python
from celery import Celery
from app.services.audit_service import get_audit_service
from app.services.database import get_db_session

@celery.task
async def cleanup_audit_logs():
    audit_service = get_audit_service()
    async for db in get_db_session():
        deleted = await audit_service.cleanup_old_logs(db)
        logger.info(f"Cleaned up {deleted} old audit logs")
        break
```

Schedule daily:
```python
celery.conf.beat_schedule = {
    'cleanup-audit-logs': {
        'task': 'tasks.cleanup_audit_logs',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
}
```

## Esempi di Query API

### Filtro per utente e periodo
```bash
curl "http://localhost:8000/api/v1/audit/?user_email=user@example.com&date_from=2025-01-01T00:00:00Z&date_to=2025-01-31T23:59:59Z"
```

### Filtro per azioni su dispositivo specifico
```bash
curl "http://localhost:8000/api/v1/audit/?resource_type=device&resource_id=ZE1ES330J9E558&action_category=device"
```

### Filtro per errori
```bash
curl "http://localhost:8000/api/v1/audit/?success=error&limit=100"
```

### Export CSV con filtri
```bash
curl "http://localhost:8000/api/v1/audit/export/csv?date_from=2025-01-01T00:00:00Z" > audit_logs.csv
```

### Statistiche mensili
```bash
curl "http://localhost:8000/api/v1/audit/stats/summary?date_from=2025-01-01T00:00:00Z&date_to=2025-01-31T23:59:59Z"
```

## Monitoraggio

### Query Utili SQL

**Log per utente (ultimi 7 giorni):**
```sql
SELECT action, COUNT(*) as count
FROM audit_logs
WHERE user_email = 'user@example.com'
  AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY action
ORDER BY count DESC;
```

**Success rate per endpoint:**
```sql
SELECT endpoint,
       COUNT(*) as total,
       SUM(CASE WHEN success = 'success' THEN 1 ELSE 0 END) as successes,
       ROUND(100.0 * SUM(CASE WHEN success = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM audit_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY endpoint
ORDER BY total DESC
LIMIT 10;
```

**Errori recenti:**
```sql
SELECT timestamp, user_email, endpoint, error_message
FROM audit_logs
WHERE success = 'error'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

**Dimensione tabella:**
```sql
SELECT
    pg_size_pretty(pg_total_relation_size('audit_logs')) as size,
    COUNT(*) as rows
FROM audit_logs;
```

## Troubleshooting

### Il middleware non logga
1. Verificare che `audit_service` sia configurato in `main.py`
2. Controllare i `exclude_paths` - potrebbero escludere troppi endpoint
3. Verificare connessione database
4. Controllare log errori: `docker-compose logs backend`

### Performance lente
1. Verificare indici database: `\d audit_logs` in psql
2. Ridurre `max_body_length` se request body grandi
3. Disabilitare `log_response_body` se non necessario
4. Aumentare `retention_days` per cleanup più frequente

### Tabella troppo grande
1. Eseguire cleanup manuale: `POST /api/v1/audit/cleanup?retention_days=30`
2. Ridurre retention policy default
3. Configurare cleanup automatico schedulato
4. Esportare e archiviare log vecchi prima del cleanup

### Export timeout
1. Ridurre periodo con filtri `date_from`/`date_to`
2. Ridurre `limit` a valori più bassi
3. Usare paginazione per export incrementali

## TODO Future Enhancements

- [ ] Ruoli e permessi per accesso audit log
- [ ] Dashboard analytics visuale con grafici
- [ ] Alert automatici su pattern anomali
- [ ] Archivio log a lungo termine (S3/Object Storage)
- [ ] Compression dei log vecchi
- [ ] Ricerca full-text su request/response data
- [ ] API webhooks per eventi audit specifici
- [ ] Integrazione con SIEM systems
- [ ] Audit trail per modifiche ai log stessi
- [ ] Firma digitale dei log per non-ripudio

## Compliance

Questo sistema può supportare requisiti di compliance per:
- **GDPR**: Tracciamento accessi a dati personali
- **ISO 27001**: Audit trail per sicurezza informazioni
- **SOC 2**: Logging e monitoring controlli
- **PCI DSS**: Tracciamento accessi a sistemi

Assicurarsi di:
1. Configurare retention appropriata per requisiti legali
2. Proteggere accesso ai log (solo admin)
3. Documentare modifiche al sistema di audit
4. Backup regolari dei log di audit
5. Crittografia at-rest per dati sensibili

# SunPulse - TODO

> **Last updated:** 2026-01-03  
> **Legend:** 🔴 Critical | ⚠️ High | 🟡 Medium | 🟢 Low

---

## 🏢 ARCHITETTURA BUILDING (PRIORITÀ ALTA)

> **Nuova architettura:** Users → Edifici → Dispositivi
> 
> L'edificio diventa l'entità centrale della piattaforma. Quando un utente accede, deve creare un edificio e poi associare i dispositivi.

### Backend - Database & Models

- [ ] **[BUILD-001]** Creare migration Alembic per tabella `buildings`
  - Campi: id, name, address, address_components (JSONB), place_id, latitude, longitude, timezone, created_at, updated_at, created_by
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-002]** Creare migration per tabella `user_buildings` (relazione N:M)
  - Campi: id, user_id, building_id, role ('owner', 'admin', 'member', 'viewer'), invited_by, joined_at
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-003]** Aggiornare tabella `devices` con FK `building_id`
  - Aggiungere colonna building_id REFERENCES buildings(id)
  - Migrare dispositivi esistenti (creare building di default)
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-004]** Creare migration per tabella `building_weather`
  - Campi: id, building_id, temperature, feels_like, humidity, pressure, wind_speed, weather_condition, weather_icon, sunrise, sunset, fetched_at
  - **Effort**: 1h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-005]** Creare modelli SQLAlchemy per Building, UserBuilding, BuildingWeather
  - File: `modules/backend/app/models/building.py`
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

### Backend - API Endpoints

- [ ] **[BUILD-006]** Endpoint CRUD Buildings
  - `GET /api/v1/buildings/` - Lista edifici dell'utente
  - `POST /api/v1/buildings/` - Crea nuovo edificio
  - `GET /api/v1/buildings/{id}` - Dettaglio edificio
  - `PUT /api/v1/buildings/{id}` - Aggiorna edificio
  - `DELETE /api/v1/buildings/{id}` - Elimina edificio
  - File: `modules/backend/app/api/v1/endpoints/buildings.py`
  - **Effort**: 4h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-007]** Endpoint gestione dispositivi per edificio
  - `GET /api/v1/buildings/{id}/devices` - Lista dispositivi
  - `POST /api/v1/buildings/{id}/devices` - Associa dispositivo
  - `DELETE /api/v1/buildings/{id}/devices/{did}` - Rimuovi dispositivo
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-008]** Endpoint gestione membri edificio
  - `GET /api/v1/buildings/{id}/members` - Lista membri
  - `POST /api/v1/buildings/{id}/members` - Invita utente
  - `DELETE /api/v1/buildings/{id}/members/{uid}` - Rimuovi membro
  - `PUT /api/v1/buildings/{id}/members/{uid}` - Aggiorna ruolo
  - **Effort**: 3h
  - **Priorità**: 🟡 Medio

- [ ] **[BUILD-009]** Endpoint Address Autocomplete (Google Places)
  - `GET /api/v1/address/autocomplete?q=...` - Ricerca indirizzi
  - `GET /api/v1/address/details/{place_id}` - Dettagli + coordinate
  - Integrazione Google Places API
  - File: `modules/backend/app/api/v1/endpoints/address.py`
  - **Effort**: 3h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-010]** Endpoint Weather per edificio
  - `GET /api/v1/buildings/{id}/weather` - Dati meteo attuali
  - `GET /api/v1/buildings/{id}/weather/history` - Storico meteo
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

### Backend - Services

- [ ] **[BUILD-011]** Creare WeatherService
  - Supporto OpenWeatherMap e WeatherAPI
  - Fetch dati meteo da coordinate GPS
  - Caching dati meteo in Redis (TTL 15 min)
  - File: `modules/backend/app/services/weather_service.py`
  - **Effort**: 4h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-012]** Creare GooglePlacesService
  - Autocomplete indirizzi
  - Geocoding (indirizzo → coordinate)
  - File: `modules/backend/app/services/google_places_service.py`
  - **Effort**: 3h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-013]** Creare task Celery `collect_weather_data`
  - Eseguire ogni 15 minuti per ogni edificio
  - Salvare dati in tabella building_weather
  - File: `modules/backend/app/tasks/weather_tasks.py`
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-014]** Aggiornare DataCollector per filtrare per building_id
  - I dati raccolti devono essere associati all'edificio
  - Aggiornare query InfluxDB per includere building_id come tag
  - **Effort**: 3h
  - **Priorità**: ⚠️ Alto

### Frontend - Pages & Components

- [ ] **[BUILD-015]** Pagina selezione/creazione edificio (Onboarding)
  - Mostrata al primo accesso se l'utente non ha edifici
  - Form creazione edificio con:
    - Campo nome edificio
    - Campo indirizzo con Google Autocomplete
    - Mappa preview della posizione
  - File: `modules/frontend/src/pages/BuildingOnboarding.tsx`
  - **Effort**: 6h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-016]** Componente AddressAutocomplete
  - Input con autocomplete Google Places
  - Preview mappa con marker
  - File: `modules/frontend/src/components/common/AddressAutocomplete.tsx`
  - **Effort**: 4h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-017]** Selettore Edificio nel Header
  - Dropdown per cambiare edificio attivo
  - Mostra nome edificio + temperatura
  - File: aggiornare `modules/frontend/src/components/layout/Header.tsx`
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-018]** Pagina gestione edifici
  - Lista edifici con card
  - Modifica nome/indirizzo
  - Gestione membri (invita/rimuovi)
  - Gestione dispositivi associati
  - File: `modules/frontend/src/pages/Buildings.tsx`
  - **Effort**: 6h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-019]** Aggiornare Dashboard per mostrare temperatura edificio
  - Card meteo con temperatura attuale
  - Icona condizioni meteo
  - Correlazione produzione/temperatura
  - **Effort**: 2h
  - **Priorità**: 🟡 Medio

- [ ] **[BUILD-020]** Aggiornare tutti gli hook per includere building_id
  - `useDevices(buildingId)`
  - `useEnergyStats(buildingId)`
  - `useRealTimeData(buildingId)`
  - **Effort**: 3h
  - **Priorità**: ⚠️ Alto

### Configurazione & Infrastruttura

- [ ] **[BUILD-021]** Aggiungere variabili ambiente per Google APIs
  - `GOOGLE_MAPS_API_KEY`
  - Aggiornare `.env.example`
  - **Effort**: 0.5h
  - **Priorità**: 🔴 Critico

- [ ] **[BUILD-022]** Aggiungere variabili ambiente per Weather API
  - `WEATHER_API_PROVIDER` (openweathermap/weatherapi)
  - `OPENWEATHERMAP_API_KEY` o `WEATHERAPI_KEY`
  - Aggiornare `.env.example`
  - **Effort**: 0.5h
  - **Priorità**: ⚠️ Alto

- [ ] **[BUILD-023]** Configurare Google Maps JS API nel frontend
  - Aggiungere script Google Maps
  - Configurare API key restrizioni
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

---

## 🔴 CRITICAL BUGS

### Backend

- [x] **[BE-001]** `useDevices.ts:62` - `stats[device.status]++` invalid in TypeScript ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/hooks/useDevices.ts`
  - Fix: Use correct increment pattern with type checking
  
- [x] **[BE-002]** `data.py:177` - `get_settings()` not imported in try block ✅ FIXED 2025-12-11
  - File: `modules/backend/app/api/v1/endpoints/data.py`
  - Fix: Moved import to top of file

- [x] **[BE-003]** `zcs_api_service.py:230` - Chunking uses 23h instead of 24h, may lose data ✅ FIXED 2025-12-11
  - File: `modules/backend/app/services/zcs_api_service.py`
  - Fix: Changed `timedelta(hours=23)` to `timedelta(hours=24)`

### Frontend

- [x] **[FE-001]** `Dashboard.tsx:27-28` - Energy estimate always 0 if `daily_energy=0` ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Added fallback to summary.total_energy_today

- [x] **[FE-002]** `Dashboard.tsx:133` - Division by zero if `stats.total=0` ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Added guard `stats.total > 0 ? ... : 0`

- [x] **[FE-003]** `DeviceCard.tsx:128` - Conversion `*1000` kWh→Wh potentially wrong ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/components/devices/DeviceCard.tsx`
  - Fix: Removed incorrect *1000 conversion

- [x] **[FE-004]** `PowerChart.tsx:39-87` - Simulated data instead of real ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/components/charts/PowerChart.tsx`
  - Fix: Implemented fetch from `/api/v1/data/historical` with fallback to simulation

---

## ⚠️ ARCHITECTURAL ISSUES

- [x] **[ARCH-001]** Auth Mock always active ✅ FIXED 2025-12-11
  - File: `modules/frontend/src/providers/AuthProvider.tsx:80`
  - Issue: `isDevelopmentMode = true` hardcoded
  - Fix: Changed to check Auth0 domain/clientId configuration

- [ ] **[ARCH-002]** No React Error Boundary
  - Fix: Create `modules/frontend/src/components/common/ErrorBoundary.tsx`

- [ ] **[ARCH-003]** Missing TypeScript types for ZCS response
  - Fix: Create `modules/frontend/src/types/zcs.ts` with complete typing

- [ ] **[ARCH-004]** Backend doesn't persist devices in DB
  - Issue: Devices generated from `thing_keys`, not saved in PostgreSQL
  - Fix: Use existing `devices` table

- [ ] **[ARCH-005]** WebSocket not implemented in backend
  - Fix: Create WebSocket endpoint for real-time updates

- [ ] **[ARCH-006]** Alarms commented out/disabled
  - File: `modules/frontend/src/components/devices/DeviceCard.tsx:172-188`
  - Fix: Re-enable alarms section with correct import

---

## 🟡 UX/UI IMPROVEMENTS

### Dashboard

- [x] **[UX-001a]** Dashboard riorganizzata ✅ DONE 2025-12-12
  - Rimosso box "Stato Dispositivi" ridondante
  - Aggiunto selettore dispositivo in alto a destra
  - Grafico espanso a tutta larghezza

- [x] **[UX-001b]** Aggiunte card bilancio energetico giornaliero ✅ DONE 2025-12-12
  - Card "Consumo Giornaliero" con suddivisione: Dal Sole, Dalla Batteria, Dalla Rete
  - Card "Produzione Giornaliera" con suddivisione: Autoconsumo, Verso Rete, Verso Batteria
  - Card "Potenza Istantanea" compatta

- [x] **[UX-001c]** Corretti campi ZCS per dati batteria ✅ FIXED 2025-12-12
  - `energyDischarging` (non `energyDischargingBat`) per energia dalla batteria
  - `energyCharging` (non `energyChargingBat`) per energia verso batteria
  - `energyAutoconsuming` per autoconsumo diretto

- [x] **[UX-001d]** Risolto refresh fastidioso del grafico ✅ FIXED 2025-12-12
  - Polling ridotto a 60 secondi
  - Componente Line memorizzato con React.memo
  - Animazioni disabilitate dopo primo render
  - Slider mantiene posizione con useRef

- [ ] **[UX-001]** Hardcoded percentage variations (`+5.2%`, `+12%`, etc.)
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Calculate from real historical data

- [ ] **[UX-002]** System efficiency fixed at 85.5%
  - Fix: Calculate from real data

- [ ] **[UX-003]** Missing loading skeleton for cards
  - Fix: Use Ant Design `<Skeleton>` during loading

- [ ] **[UX-004]** Missing manual dashboard refresh button
  - Fix: Add `<Button>` with `onClick={refetch}`

- [ ] **[UX-005]** Last update timestamp not visible
  - Fix: Show "Last updated: X minutes ago"

### DeviceList

- [ ] **[UX-006]** Cards too narrow on XL screens (`xl={4}`)
  - File: `modules/frontend/src/components/devices/DeviceList.tsx:251`
  - Fix: Change to `xl={6}` or make configurable

- [ ] **[UX-007]** No infinite scroll/virtualization
  - Fix: Implement virtual list for performance

### Header

- [x] **[UX-008]** Notification count hardcoded to 3 ✅ FIXED 2025-12-12
  - File: `modules/frontend/src/components/layout/Header.tsx`
  - Fix: Rimossa campanella con badge finto (sistema notifiche non implementato)

- [x] **[UX-009]** User menu overflow ✅ FIXED 2025-12-12
  - Fix: Aggiunto ellipsis e maxWidth per nome/email utente

### Mobile

- [ ] **[UX-010]** Header stats visible on mobile (clutters UI)
  - Fix: Add `mobile-hidden` class to stats

- [ ] **[UX-011]** Chart slider difficult on touch
  - Fix: Increase touch area or disable on mobile

---

## 🚀 NEW FEATURES

### Scansione Bollette

- [ ] **[FEAT-001]** Scansione e OCR bollette elettriche
  - **Descrizione**: Permette all'utente di caricare foto/PDF delle bollette e estrarre automaticamente i dati
  - **Componenti**:
    - [ ] Upload immagine/PDF (frontend)
    - [ ] Servizio OCR (Tesseract / Google Vision / AWS Textract)
    - [ ] Parser per estrarre dati strutturati (consumo kWh, costi, periodo, fornitore)
    - [ ] Modello database per bollette
    - [ ] API endpoints CRUD bollette
    - [ ] Pagina storico bollette con grafici
    - [ ] Confronto bollette vs produzione fotovoltaico
  - **Effort stimato**: 16-24h
  - **Priorità**: Media

### Status Page

- [ ] **[FEAT-002]** Pagina Status Servizi tipo Statuspage
  - **Descrizione**: Pagina pubblica che mostra lo stato di tutti i servizi interni e esterni con storico uptime
  - **Componenti**:
    - [ ] Endpoint backend `/api/v1/status/services` - stato tutti i servizi
    - [ ] Endpoint backend `/api/v1/status/history` - storico uptime (24h, 7d, 30d)
    - [ ] Modello database per storico check (timestamp, service, status, latency)
    - [ ] Task Celery per health check periodico (ogni 1 min)
    - [ ] Pagina frontend `/status` con:
      - [ ] Badge stato per ogni servizio (🟢 Operational, 🟡 Degraded, 🔴 Outage)
      - [ ] Uptime percentage (99.9%)
      - [ ] Latency media
      - [ ] Grafico storico uptime (barre orizzontali tipo statuspage.io)
      - [ ] Incidenti recenti con timeline
  - **Servizi da monitorare**:
    - PostgreSQL
    - InfluxDB
    - Redis
    - Auth Service
    - Backend API
    - Celery Workers
    - ZCS Azzurro API (esterno)
    - Resend Email (esterno)
  - **Effort stimato**: 8-12h
  - **Priorità**: Media

### Documentazione

- [ ] **[FEAT-003]** Collezione Postman/Bruno per API
  - **Descrizione**: File di collezione che documenta tutti gli endpoint API per testing e sviluppo
  - **Componenti**:
    - [ ] File `doc/api/sunpulse.postman_collection.json`
    - [ ] File `doc/api/sunpulse.bruno/` (cartella Bruno)
    - [ ] Variabili ambiente (dev, prod)
    - [ ] Esempi request/response per ogni endpoint
    - [ ] Test automatici per validazione response
  - **Endpoints da documentare**:
    - [ ] Health (4 endpoints)
    - [ ] Devices (4 endpoints)
    - [ ] Data (6 endpoints)
    - [ ] Alarms (5 endpoints)
    - [ ] Tasks (8 endpoints)
    - [ ] Notifications (4 endpoints)
  - **Effort stimato**: 4-6h
  - **Priorità**: Alta
  - **Nota**: ⚠️ Aggiornare ad ogni nuovo endpoint!

- [ ] **[FEAT-004]** Documentazione Utente Completa
  - **Descrizione**: Guida utente completa per l'utilizzo della piattaforma SunPulse
  - **Componenti**:
    - [ ] `doc/user-guide/` cartella documentazione
    - [ ] README con indice navigabile
    - [ ] Guida installazione e primo avvio
    - [ ] Tour delle funzionalità (Dashboard, Dispositivi, Analytics, Allarmi, Impostazioni)
    - [ ] FAQ e troubleshooting
    - [ ] Screenshot annotati per ogni sezione
    - [ ] Video tutorial (opzionale)
  - **Sezioni**:
    - [ ] 1. Introduzione e requisiti
    - [ ] 2. Installazione e configurazione
    - [ ] 3. Primo accesso e setup Auth0
    - [ ] 4. Dashboard - Panoramica sistema
    - [ ] 5. Dispositivi - Gestione e monitoraggio
    - [ ] 6. Analytics - Analisi dati storici
    - [ ] 7. Allarmi - Gestione notifiche
    - [ ] 8. Impostazioni - Configurazione sistema
    - [ ] 9. API - Integrazione esterna
    - [ ] 10. Troubleshooting
  - **Effort stimato**: 8-12h
  - **Priorità**: Media

### Caching e Persistenza Dati

- [ ] **[FEAT-006]** Strategia Caching e Persistenza Dati Storici
  - **Descrizione**: Implementare persistenza dati storici in PostgreSQL per evitare chiamate API ZCS ripetute
  - **Componenti**:
    - [ ] Tabella `daily_energy` in PostgreSQL (schema già definito)
    - [ ] Tabella `alarm_history` per storico allarmi
    - [ ] Task Celery `collect_daily_energy` (ogni giorno 00:05)
    - [ ] Task Celery `collect_alarms` (ogni ora)
    - [ ] Task Celery `cleanup_cache` (pulizia vecchia)
    - [ ] Endpoint API per query dati storici da DB (non da ZCS)
    - [ ] Migration Alembic per nuove tabelle
  - **Benefici**:
    - Meno chiamate all'API ZCS (rate limiting)
    - Dati storici sempre disponibili (anche se ZCS offline)
    - Performance migliori per Analytics
    - Backup dati per report e fatturazione
  - **Effort stimato**: 8-12h
  - **Priorità**: Alta

### Lettura Contatore Gas

- [ ] **[FEAT-007]** Lettura Contatore Gas con OCR
  - **Descrizione**: Permette all'utente di registrare le letture del contatore gas, sia manualmente che tramite riconoscimento automatico da foto (OCR)
  - **Modalità di input**:
    - [ ] Inserimento manuale: form con valore lettura, data, note
    - [ ] OCR da foto: upload immagine del contatore, riconoscimento automatico cifre
  - **Componenti Backend**:
    - [ ] Modello database `MeterReading` (gas, estendibile a luce/acqua)
    - [ ] Servizio OCR (`TesseractOCR` o `Google Cloud Vision`)
    - [ ] Pre-processing immagine (crop, contrast, threshold)
    - [ ] Validazione lettura (non può essere < precedente)
    - [ ] API endpoints CRUD letture
  - **Componenti Frontend**:
    - [ ] Nuova pagina `/meters` (Contatori)
    - [ ] Form inserimento manuale con validazione
    - [ ] Upload foto con preview e crop
    - [ ] Conferma/correzione valore OCR
    - [ ] Storico letture con tabella e grafici
    - [ ] Calcolo consumo tra letture
    - [ ] Export dati CSV
  - **API Endpoints**:
    - [ ] `POST /api/v1/meters/readings` - Nuova lettura manuale
    - [ ] `POST /api/v1/meters/readings/ocr` - Upload foto e OCR
    - [ ] `GET /api/v1/meters/readings` - Lista letture
    - [ ] `GET /api/v1/meters/readings/{id}` - Dettaglio lettura
    - [ ] `PUT /api/v1/meters/readings/{id}` - Modifica lettura
    - [ ] `DELETE /api/v1/meters/readings/{id}` - Elimina lettura
    - [ ] `GET /api/v1/meters/consumption` - Calcolo consumi
  - **Modello Dati**:
    ```sql
    meter_readings (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id),
      meter_type VARCHAR(20) NOT NULL,  -- 'gas', 'electricity', 'water'
      reading_value DECIMAL(12,3) NOT NULL,
      reading_date DATE NOT NULL,
      reading_time TIME,
      source VARCHAR(20) NOT NULL,      -- 'manual', 'ocr'
      image_path VARCHAR(500),
      ocr_confidence DECIMAL(3,2),
      notes TEXT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP,
      UNIQUE(user_id, meter_type, reading_date)
    );
    ```
  - **Opzioni OCR**:
    - Tesseract (self-hosted, gratuito)
    - Google Cloud Vision (più preciso, ~€1.50/1000 immagini)
    - EasyOCR (Python, buono per cifre)
  - **Effort stimato**: 12-16h
  - **Priorità**: Media-Alta

### Audit Log

- [ ] **[FEAT-005]** Sistema Audit Log Completo
  - **Descrizione**: Tracciamento di tutte le azioni utente e di sistema per compliance e debugging
  - **Nota**: Tabella `audit_log` già esiste in PostgreSQL, da implementare middleware e UI
  - **Componenti Backend**:
    - [ ] Middleware FastAPI per logging automatico delle richieste
    - [ ] Servizio `AuditService` per scrittura log
    - [ ] Endpoint API per query log (`GET /api/v1/audit/`)
    - [ ] Filtri: per utente, azione, risorsa, periodo
    - [ ] Retention policy (es. 90 giorni)
  - **Componenti Frontend**:
    - [ ] Pagina `/admin/audit` (solo admin)
    - [ ] Tabella con ricerca e filtri
    - [ ] Export CSV/JSON
    - [ ] Dettaglio singola azione
  - **Azioni da tracciare**:
    - [ ] Login/Logout utente
    - [ ] Modifiche impostazioni
    - [ ] Acknowledge allarmi
    - [ ] Trigger task manuali
    - [ ] Invio email/notifiche
    - [ ] Accesso dati dispositivi
    - [ ] Errori API critici
  - **Effort stimato**: 6-8h
  - **Priorità**: Media

---

## 🟢 NICE TO HAVE

- [ ] **[NICE-001]** Dark mode theme
- [ ] **[NICE-002]** Internationalization (i18n)
- [ ] **[NICE-003]** Pull-to-refresh on mobile
- [ ] **[NICE-004]** Toast notifications for API errors
- [ ] **[NICE-005]** Empty states with illustrations
- [ ] **[NICE-006]** Page transition animations
- [ ] **[NICE-007]** PWA support (service worker)
- [ ] **[NICE-008]** Data export CSV/PDF

---

## 📋 PAGES TO COMPLETE

- [x] **[PAGE-001]** Device Detail Page (`/devices/:id`) ✅ DONE 2025-12-12
  - Effort: 4h
  - File: `modules/frontend/src/pages/DeviceDetail.tsx`
  
- [x] **[PAGE-002]** Analytics Page (`/analytics`) ✅ DONE 2025-12-12
  - Effort: 6h
  - File: `modules/frontend/src/pages/Analytics.tsx`
  - Grafici produzione/consumo, selettore periodo, KPI, tabelle riepilogo
  
- [x] **[PAGE-003]** Alarms Page (`/alarms`) ✅ DONE 2025-12-12
  - Effort: 4h
  - File: `modules/frontend/src/pages/Alarms.tsx`
  - Lista allarmi, filtri, statistiche, gestione stato
  
- [x] **[PAGE-004]** Settings Page (`/settings`) ✅ DONE 2025-12-12
  - Effort: 3h
  - File: `modules/frontend/src/pages/Settings.tsx`
  - Tabs: Generale, Notifiche, Dispositivi, API, Sistema

- [ ] **[PAGE-005]** ⚠️ Verificare/Implementare persistenza Settings
  - **Stato attuale**: La pagina Settings è solo UI, i dati NON vengono salvati
  - **Da verificare/implementare**:
    - [ ] Endpoint backend `GET/PUT /api/v1/settings/` per CRUD impostazioni
    - [ ] Modello database per settings utente
    - [ ] Frontend: collegare form a API reali (attualmente mock)
    - [ ] Test: modificare impostazione → riavviare → verificare persistenza
  - **Impostazioni da persistere**:
    - [ ] Generale: nome sistema, timezone, valuta, lingua
    - [ ] Notifiche: email, frequenza report, soglie allarmi
    - [ ] Dispositivi: nomi custom, soglie alert per dispositivo
    - [ ] API: chiavi ZCS (solo visualizzazione, no modifica)
  - **Effort stimato**: 4-6h
  - **Priorità**: Alta

---

## 🔧 INFRASTRUCTURE

- [ ] **[INFRA-001]** Remove Mosquitto if unused
- [ ] **[INFRA-002]** Configure external network for multi-compose
- [ ] **[INFRA-003]** Pattern `env_dev → .env`
- [ ] **[INFRA-004]** SSL/HTTPS configuration
- [ ] **[INFRA-005]** Prometheus metrics
- [ ] **[INFRA-006]** CI/CD pipeline

---

## 📊 SUMMARY

| Priority | Count | Status |
|----------|-------|--------|
| 🏢 **Building Architecture** | **23** | **0/23** ⚡ NEW |
| 🔴 Critical | 7 | **7/7 completed** ✅ |
| ⚠️ High | 6 | 1/6 completed |
| 🟡 Medium | 15 | **6/15 completed** |
| 🟢 Low | 8 | 0/8 completed |
| 🚀 New Features | 7 | 0/7 completed |
| 📋 Pages | 5 | 4/5 completed |
| 🔧 Infra | 6 | 0/6 completed |
| **TOTAL** | **77** | **18/77** |

### 🏢 Building Architecture Breakdown

| Categoria | Task | Effort Stimato |
|-----------|------|----------------|
| Database & Models | BUILD-001 → BUILD-005 | ~7h |
| API Endpoints | BUILD-006 → BUILD-010 | ~14h |
| Services | BUILD-011 → BUILD-014 | ~12h |
| Frontend | BUILD-015 → BUILD-020 | ~23h |
| Configurazione | BUILD-021 → BUILD-023 | ~2h |
| **TOTALE** | **23 task** | **~58h** |

---

## 📝 NOTES

- Prioritize critical bug fixes before new features
- Code review completed on 2025-12-11
- Both backend and frontend have issues to resolve
- **2025-12-12**: Dashboard riorganizzata, corretti campi ZCS per batteria, risolto refresh grafico
- **2025-12-12**: Completate tutte le 4 pagine mancanti (DeviceDetail, Analytics, Alarms, Settings)
- **2025-12-19**: Creato manuale utente (`doc/MANUALE_UTENTE.md`) con documentazione API ZCS completa
- **2025-12-19**: Definita strategia caching (FEAT-006) per persistenza dati storici
- **2025-12-19**: Fix priorità dati storici vs realtime per energia giornaliera (usa TotalDecimal)
- **2025-12-19**: Deploy HTTPS con Traefik + Let's Encrypt completato
- **2025-12-19**: Aggiunta FEAT-007 - Lettura Contatore Gas con OCR
- **2026-01-03**: 🏢 **ARCHITETTURA BUILDING** - Introdotto concetto di Edificio come entità centrale
  - Nuovo schema: Users → Edifici → Dispositivi
  - Più utenti possono accedere allo stesso edificio
  - Servizio temperatura automatico per ogni edificio
  - Google Places Autocomplete per ricerca indirizzi
  - 23 nuovi task aggiunti (stimati ~58h di lavoro)

# SunPulse - TODO

> **Last updated:** 2026-01-03  
> **Legend:** 🔴 Critical | ⚠️ High | 🟡 Medium | 🟢 Low

---

## 🏢 ARCHITETTURA BUILDING (PRIORITÀ ALTA)

> **Nuova architettura:** Users → Edifici → Dispositivi
> 
> L'edificio diventa l'entità centrale della piattaforma. Quando un utente accede, deve creare un edificio e poi associare i dispositivi.

### Backend - Database & Models

- [x] **[BUILD-001]** Creare migration per tabella `buildings` ✅ 2026-01-03
  - Campi: id, name, address, address_components (JSONB), place_id, latitude, longitude, timezone, created_at, updated_at, created_by
  - File: `modules/postgres/init/02-buildings.sql`
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

- [x] **[BUILD-002]** Creare migration per tabella `user_buildings` (relazione N:M) ✅ 2026-01-03
  - Campi: id, user_id, building_id, role ('owner', 'admin', 'member', 'viewer'), invited_by, joined_at
  - File: `modules/postgres/init/02-buildings.sql`
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

- [x] **[BUILD-003]** Creare tabella `building_devices` per associazione edificio-dispositivo ✅ 2026-01-03
  - Campi: id, building_id, thing_key, name, device_type, status, last_seen
  - Migrare dispositivi esistenti (creare building di default)
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

- [x] **[BUILD-004]** Creare migration per tabella `building_weather` ✅ 2026-01-03
  - Campi: id, building_id, temperature, feels_like, humidity, pressure, wind_speed, weather_condition, weather_icon, sunrise, sunset, fetched_at
  - File: `modules/postgres/init/02-buildings.sql`
  - **Effort**: 1h
  - **Priorità**: ⚠️ Alto

- [x] **[BUILD-005]** Creare modelli SQLAlchemy per Building, UserBuilding, BuildingWeather ✅ 2026-01-03
  - File: `modules/backend/app/models/building.py`
  - Include anche: BuildingDevice, UserOnboarding
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

### Backend - API Endpoints

- [x] **[BUILD-006]** Endpoint CRUD Buildings ✅ 2026-01-03
  - File: `modules/backend/app/api/v1/endpoints/buildings.py`
  - `GET /api/v1/buildings/` - Lista edifici dell'utente
  - `POST /api/v1/buildings/` - Crea nuovo edificio
  - `GET /api/v1/buildings/{id}` - Dettaglio edificio
  - `PUT /api/v1/buildings/{id}` - Aggiorna edificio
  - `DELETE /api/v1/buildings/{id}` - Elimina edificio
  - File: `modules/backend/app/api/v1/endpoints/buildings.py`
  - **Effort**: 4h
  - **Priorità**: 🔴 Critico

- [x] **[BUILD-007]** Endpoint gestione dispositivi per edificio ✅ 2026-01-03
  - `GET /api/v1/buildings/{id}/devices` - Lista dispositivi
  - `POST /api/v1/buildings/{id}/devices` - Associa dispositivo
  - `DELETE /api/v1/buildings/{id}/devices/{did}` - Rimuovi dispositivo
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

- [x] **[BUILD-008]** Endpoint gestione membri edificio ✅ 2026-01-03
  - `GET /api/v1/buildings/{id}/members` - Lista membri
  - `POST /api/v1/buildings/{id}/members` - Invita utente
  - `DELETE /api/v1/buildings/{id}/members/{uid}` - Rimuovi membro
  - `PUT /api/v1/buildings/{id}/members/{uid}` - Aggiorna ruolo
  - **Effort**: 3h
  - **Priorità**: 🟡 Medio

- [x] **[BUILD-009]** Endpoint Address Autocomplete (Google Places) ✅ 2026-01-03
  - File: `modules/backend/app/services/google_places_service.py`
  - `GET /api/v1/buildings/address/autocomplete?q=...` - Ricerca indirizzi
  - `GET /api/v1/address/details/{place_id}` - Dettagli + coordinate
  - Integrazione Google Places API
  - File: `modules/backend/app/api/v1/endpoints/address.py`
  - **Effort**: 3h
  - **Priorità**: 🔴 Critico

- [x] **[BUILD-010]** Endpoint Weather per edificio ✅ 2026-01-03
  - `GET /api/v1/buildings/{id}/weather` - Dati meteo attuali
  - `GET /api/v1/buildings/{id}/weather/history` - Storico meteo
  - `POST /api/v1/buildings/{id}/weather/refresh` - Forza aggiornamento
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

### Backend - Services

- [x] **[BUILD-011]** Creare WeatherService ✅ 2026-01-03
  - File: `modules/backend/app/services/weather_service.py`
  - Supporto OpenWeatherMap e WeatherAPI
  - Fetch dati meteo da coordinate GPS
  - File: `modules/backend/app/services/weather_service.py`
  - **Effort**: 4h
  - **Priorità**: ⚠️ Alto

- [x] **[BUILD-012]** Creare GooglePlacesService ✅ 2026-01-03
  - File: `modules/backend/app/services/google_places_service.py`
  - Autocomplete indirizzi
  - Geocoding (indirizzo → coordinate)
  - Get timezone da coordinate
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

### Wizard di Onboarding

- [x] **[WIZARD-001]** Creare migration per tabella `user_onboarding` ✅ 2026-01-03
  - File: `modules/postgres/init/02-buildings.sql`
  - Campi: id, user_id, current_step, status, building_id, step_data (JSONB), completed_at, created_at, updated_at
  - **Effort**: 0.5h
  - **Priorità**: 🔴 Critico

- [x] **[WIZARD-002]** Creare modello SQLAlchemy per UserOnboarding ✅ 2026-01-03
  - File: `modules/backend/app/models/building.py` (incluso con Building)
  - **Effort**: 0.5h
  - **Priorità**: 🔴 Critico

- [x] **[WIZARD-003]** Creare OnboardingService ✅ 2026-01-03
  - File: `modules/backend/app/services/onboarding_service.py`
  - Logica per gestione stato wizard
  - Validazione dispositivi via API ZCS
  - File: `modules/backend/app/services/onboarding_service.py`
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

- [x] **[WIZARD-004]** Endpoint API Onboarding ✅ 2026-01-03
  - File: `modules/backend/app/api/v1/endpoints/onboarding.py`
  - `GET /api/v1/onboarding/status` - Stato wizard utente
  - `PUT /api/v1/onboarding/step/{step}` - Salva progresso step
  - `POST /api/v1/onboarding/complete` - Marca completato
  - `POST /api/v1/onboarding/skip` - Salta wizard
  - `POST /api/v1/onboarding/validate-device` - Valida thing_key
  - File: `modules/backend/app/api/v1/endpoints/onboarding.py`
  - **Effort**: 3h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-005]** Componente WizardContainer
  - Layout con stepper e progress bar
  - Navigazione tra step (Avanti/Indietro)
  - Responsive design
  - File: `modules/frontend/src/components/wizard/WizardContainer.tsx`
  - **Effort**: 3h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-006]** Step 1: Benvenuto
  - Pagina introduttiva con branding
  - Breve descrizione funzionalità
  - CTA "Inizia configurazione"
  - File: `modules/frontend/src/components/wizard/StepWelcome.tsx`
  - **Effort**: 1h
  - **Priorità**: ⚠️ Alto

- [ ] **[WIZARD-007]** Step 2: Creazione Edificio
  - Form con nome edificio
  - Campo indirizzo con Google Autocomplete
  - Mappa preview con marker
  - Auto-detect timezone
  - File: `modules/frontend/src/components/wizard/StepBuilding.tsx`
  - **Effort**: 4h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-008]** Step 3: Aggiunta Dispositivi
  - Form con Thing Key e nome dispositivo
  - Validazione real-time via API ZCS
  - Lista dispositivi aggiunti con rimozione
  - Pulsante "+ Aggiungi altro"
  - Minimo 1 dispositivo richiesto
  - File: `modules/frontend/src/components/wizard/StepDevices.tsx`
  - **Effort**: 4h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-009]** Step 4: Configurazione Notifiche
  - Campo email
  - Toggle per tipi di notifiche
  - Step opzionale con "Configura dopo"
  - File: `modules/frontend/src/components/wizard/StepNotifications.tsx`
  - **Effort**: 2h
  - **Priorità**: 🟡 Medio

- [ ] **[WIZARD-010]** Step 5: Riepilogo
  - Sommario configurazione completata
  - Lista edificio e dispositivi
  - Stato notifiche
  - CTA "Vai alla Dashboard"
  - Animazione celebrativa (confetti/success)
  - File: `modules/frontend/src/components/wizard/StepSummary.tsx`
  - **Effort**: 2h
  - **Priorità**: ⚠️ Alto

- [ ] **[WIZARD-011]** Hook useOnboarding
  - Gestione stato wizard
  - Chiamate API per salvataggio progresso
  - Navigazione tra step
  - File: `modules/frontend/src/hooks/useOnboarding.ts`
  - **Effort**: 2h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-012]** Pagina Wizard (/onboarding)
  - Route protetta per utenti senza edifici
  - Redirect automatico se wizard non completato
  - File: `modules/frontend/src/pages/Onboarding.tsx`
  - **Effort**: 1h
  - **Priorità**: 🔴 Critico

- [ ] **[WIZARD-013]** Logica redirect nel ProtectedRoute
  - Se utente loggato e wizard non completato → redirect a /onboarding
  - Se wizard completato → accesso normale
  - Aggiornare: `modules/frontend/src/components/common/ProtectedRoute.tsx`
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

- [x] **[FEAT-006]** Strategia Caching e Persistenza Dati Storici ✅ PARZIALMENTE COMPLETATO
  - **Descrizione**: Implementare persistenza dati storici in PostgreSQL per evitare chiamate API ZCS ripetute
  - **Componenti**:
    - [x] Tabella `daily_energy` in PostgreSQL ✅ 2025-12-11
    - [x] Task Celery `collect_daily_energy` (ogni giorno 00:05) ✅ 2025-12-11
    - [x] Task Celery `cleanup_old_cache` (pulizia cache) ✅ 2025-12-11
    - [ ] Tabella `alarm_history` per storico allarmi
    - [ ] Endpoint API per query dati storici da DB (non da ZCS)
    - [ ] Migration Alembic per nuove tabelle
  - **Benefici**:
    - Meno chiamate all'API ZCS (rate limiting)
    - Dati storici sempre disponibili (anche se ZCS offline)
    - Performance migliori per Analytics
    - Backup dati per report e fatturazione

### Report Email Automatici

- [x] **[FEAT-008]** Sistema Notifiche Email Completo ✅ COMPLETATO 2025-12-11
  - **Descrizione**: Invio automatico di report e notifiche via email basato su preferenze utente
  - **Componenti Implementati**:
    - [x] Template email report giornaliero (HTML responsive)
    - [x] Template email report settimanale (con tabella 7 giorni)
    - [x] Template email allarme (critical/warning/info)
    - [x] Task Celery `send_daily_email_report` (ogni giorno 20:00 CET)
    - [x] Task Celery `send_weekly_email_report` (domenica 10:00 CET)
    - [x] Trigger automatico email su allarmi (collect_alarm_data)
    - [x] Email destinatario da impostazioni utente (PostgreSQL)
    - [x] Anti-spam: allarmi notificati una sola volta (cache 24h)
  - **Integrazione con Resend**:
    - [x] Servizio email configurato in `email_service.py`
    - [x] API endpoints per test e invio manuale
  - **Effort**: 6h
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

- [x] **[PAGE-005]** ✅ Implementata persistenza Settings (2025-12-11)
  - **Stato**: COMPLETATO
  - **Implementato**:
    - [x] Endpoint backend `GET/PUT /api/v1/settings/` per CRUD impostazioni
    - [x] Modello database `UserSettings` legato a user_id (Auth0 sub)
    - [x] Frontend: collegato form a API reali con React Query
    - [x] Persistenza in PostgreSQL
  - **Impostazioni persistite**:
    - [x] Generale: nome sistema, timezone, valuta, lingua, tariffe energia
    - [x] Notifiche: email, report giornaliero/settimanale, soglie allarmi
    - [x] Dispositivi: stato online/offline in tempo reale
    - [x] API: stato connessione ZCS, ultimo sync

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
| 🧙 **Wizard Onboarding** | **13** | **0/13** ⚡ NEW |
| 🔴 Critical | 7 | **7/7 completed** ✅ |
| ⚠️ High | 6 | 1/6 completed |
| 🟡 Medium | 15 | **6/15 completed** |
| 🟢 Low | 8 | 0/8 completed |
| 🚀 New Features | 8 | **2/8 completed** |
| 📋 Pages | 5 | **5/5 completed** ✅ |
| 🔧 Infra | 6 | 0/6 completed |
| **TOTAL** | **90** | **18/90** |

### 🏢 Building Architecture Breakdown

| Categoria | Task | Effort Stimato |
|-----------|------|----------------|
| Database & Models | BUILD-001 → BUILD-005 | ✅ 5/5 completati |
| API Endpoints | BUILD-006 → BUILD-010 | ✅ 5/5 completati |
| Services | BUILD-011 → BUILD-014 | ✅ 2/4 completati |
| Frontend | BUILD-015 → BUILD-020 | ~23h |
| Configurazione | BUILD-021 → BUILD-023 | ~2h |
| **TOTALE** | **23 task** | **~58h** |

### 🧙 Wizard Onboarding Breakdown

| Categoria | Task | Effort Stimato |
|-----------|------|----------------|
| Database & Models | WIZARD-001, WIZARD-002 | ✅ 2/2 completati |
| Backend Services | WIZARD-003, WIZARD-004 | ✅ 2/2 completati |
| Frontend Components | WIZARD-005 → WIZARD-010 | 0/6 completati |
| Hooks & Routing | WIZARD-011 → WIZARD-013 | ~4h |
| **TOTALE** | **13 task** | **~26h** |

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
- **2025-12-11**: Implementata persistenza Settings in PostgreSQL (FEAT-005 parziale)
- **2025-12-11**: Implementato sistema notifiche email automatiche completo (FEAT-008):
  - Report giornaliero (ogni giorno 20:00 CET)
  - Report settimanale (domenica 10:00 CET)
  - Trigger automatico email su allarmi critici/warning
  - Anti-spam con cache 24h per evitare duplicati
- **2026-01-03**: 🏢 **ARCHITETTURA BUILDING** - Introdotto concetto di Edificio come entità centrale
  - Nuovo schema: Users → Edifici → Dispositivi
  - Più utenti possono accedere allo stesso edificio
  - Servizio temperatura automatico per ogni edificio
  - Google Places Autocomplete per ricerca indirizzi
  - 23 nuovi task aggiunti (stimati ~58h di lavoro)
- **2026-01-03**: 🧙 **WIZARD ONBOARDING** - Aggiunto wizard iniziale per nuovi utenti
  - 5 step: Benvenuto → Edificio → Dispositivi → Notifiche → Riepilogo
  - Validazione dispositivi real-time via API ZCS
  - Progresso salvato e ripristinabile
  - Redirect automatico se wizard non completato
  - 13 nuovi task aggiunti (stimati ~26h di lavoro)

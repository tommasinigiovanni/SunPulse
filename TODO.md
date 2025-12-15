# SunPulse - TODO

> **Last updated:** 2025-12-12  
> **Legend:** 🔴 Critical | ⚠️ High | 🟡 Medium | 🟢 Low

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
| 🔴 Critical | 7 | **7/7 completed** ✅ |
| ⚠️ High | 6 | 1/6 completed |
| 🟡 Medium | 15 | **6/15 completed** |
| 🟢 Low | 8 | 0/8 completed |
| 🚀 New Features | 1 | 0/1 completed |
| 📋 Pages | 4 | **4/4 completed** ✅ |
| 🔧 Infra | 6 | 0/6 completed |
| **TOTAL** | **47** | **18/47** |

---

## 📝 NOTES

- Prioritize critical bug fixes before new features
- Code review completed on 2025-12-11
- Both backend and frontend have issues to resolve
- **2025-12-12**: Dashboard riorganizzata, corretti campi ZCS per batteria, risolto refresh grafico
- **2025-12-12**: Completate tutte le 4 pagine mancanti (DeviceDetail, Analytics, Alarms, Settings)

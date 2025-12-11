# SunPulse - TODO

> **Ultimo aggiornamento:** 2025-12-11  
> **Legenda:** 🔴 Critico | ⚠️ Alto | 🟡 Medio | 🟢 Basso

---

## 🔴 BUG CRITICI

### Backend

- [ ] **[BE-001]** `useDevices.ts:62` - `stats[device.status]++` non valido in TypeScript
  - File: `modules/frontend/src/hooks/useDevices.ts`
  - Fix: Usare pattern corretto per incremento
  
- [ ] **[BE-002]** `data.py:177` - `get_settings()` non importato nel blocco try
  - File: `modules/backend/app/api/v1/endpoints/data.py`
  - Fix: Spostare import `from ....config.settings import get_settings` in alto nel file

- [ ] **[BE-003]** `zcs_api_service.py:230` - Chunking usa 23h invece di 24h, può perdere dati
  - File: `modules/backend/app/services/zcs_api_service.py`
  - Fix: Cambiare `timedelta(hours=23)` in `timedelta(hours=24)`

### Frontend

- [ ] **[FE-001]** `Dashboard.tsx:27-28` - Stima energia sempre 0 se `daily_energy=0`
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Aggiungere null safety check

- [ ] **[FE-002]** `Dashboard.tsx:133` - Division by zero se `stats.total=0`
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Aggiungere guard `stats.total > 0 ? ... : 0`

- [ ] **[FE-003]** `DeviceCard.tsx:128` - Conversione `*1000` kWh→Wh potenzialmente errata
  - File: `modules/frontend/src/components/devices/DeviceCard.tsx`
  - Fix: Verificare unità dati ZCS e correggere

- [ ] **[FE-004]** `PowerChart.tsx:39-87` - Dati simulati invece che reali
  - File: `modules/frontend/src/components/charts/PowerChart.tsx`
  - Fix: Implementare fetch da `/api/v1/data/historical`

---

## ⚠️ PROBLEMI ARCHITETTURALI

- [ ] **[ARCH-001]** Auth Mock sempre attivo
  - File: `modules/frontend/src/providers/AuthProvider.tsx:80`
  - Problema: `isDevelopmentMode = true` hardcoded
  - Fix: Leggere da env `VITE_AUTH_MOCK=true`

- [ ] **[ARCH-002]** Nessun Error Boundary React
  - Fix: Creare `modules/frontend/src/components/common/ErrorBoundary.tsx`

- [ ] **[ARCH-003]** Missing TypeScript types per ZCS response
  - Fix: Creare `modules/frontend/src/types/zcs.ts` con tipizzazione completa

- [ ] **[ARCH-004]** Backend non persiste devices in DB
  - Problema: Devices generati da `thing_keys`, non salvati in PostgreSQL
  - Fix: Usare tabella `devices` esistente

- [ ] **[ARCH-005]** WebSocket non implementato backend
  - Fix: Creare endpoint WebSocket per real-time updates

- [ ] **[ARCH-006]** Allarmi commentati/disabilitati
  - File: `modules/frontend/src/components/devices/DeviceCard.tsx:172-188`
  - Fix: Riabilitare sezione allarmi con import corretto

---

## 🟡 UX/UI IMPROVEMENTS

### Dashboard

- [ ] **[UX-001]** Percentuali variazione hardcoded (`+5.2%`, `+12%`, etc.)
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Calcolare da dati storici reali

- [ ] **[UX-002]** Efficienza sistema fissa a 85.5%
  - Fix: Calcolare da dati reali

- [ ] **[UX-003]** Manca loading skeleton per cards
  - Fix: Usare `<Skeleton>` di Ant Design durante loading

- [ ] **[UX-004]** Manca bottone refresh manuale dashboard
  - Fix: Aggiungere `<Button>` con `onClick={refetch}`

- [ ] **[UX-005]** Timestamp ultimo aggiornamento non visibile
  - Fix: Mostrare "Ultimo aggiornamento: X minuti fa"

### DeviceList

- [ ] **[UX-006]** Card troppo strette su schermi XL (`xl={4}`)
  - File: `modules/frontend/src/components/devices/DeviceList.tsx:251`
  - Fix: Cambiare in `xl={6}` o rendere configurabile

- [ ] **[UX-007]** No infinite scroll/virtualization
  - Fix: Implementare virtual list per performance

### Header

- [ ] **[UX-008]** Notifiche count hardcoded a 3
  - File: `modules/frontend/src/components/layout/Header.tsx:57`
  - Fix: Collegare a sistema notifiche reale

- [ ] **[UX-009]** Quick stats overflow su mobile
  - Fix: Nascondere stats header su viewport < 768px

### Mobile

- [ ] **[UX-010]** Header stats visibili su mobile (affollano UI)
  - Fix: Aggiungere classe `mobile-hidden` agli stats

- [ ] **[UX-011]** Grafico slider difficile su touch
  - Fix: Aumentare area touch o disabilitare su mobile

---

## 🟢 NICE TO HAVE

- [ ] **[NICE-001]** Dark mode theme
- [ ] **[NICE-002]** Internazionalizzazione (i18n)
- [ ] **[NICE-003]** Pull-to-refresh su mobile
- [ ] **[NICE-004]** Toast notifications per errori API
- [ ] **[NICE-005]** Empty state con illustrazioni
- [ ] **[NICE-006]** Animazioni transizione pagine
- [ ] **[NICE-007]** PWA support (service worker)
- [ ] **[NICE-008]** Export dati CSV/PDF

---

## 📋 PAGINE DA COMPLETARE

- [ ] **[PAGE-001]** Device Detail Page (`/devices/:id`)
  - Effort: 4h
  
- [ ] **[PAGE-002]** Analytics Page (`/analytics`)
  - Effort: 6h
  
- [ ] **[PAGE-003]** Alarms Page (`/alarms`)
  - Effort: 4h
  
- [ ] **[PAGE-004]** Settings Page (`/settings`)
  - Effort: 3h

---

## 🔧 INFRASTRUTTURA

- [ ] **[INFRA-001]** Rimuovere Mosquitto se non usato
- [ ] **[INFRA-002]** Configurare network external per multi-compose
- [ ] **[INFRA-003]** Pattern `env_dev → .env`
- [ ] **[INFRA-004]** SSL/HTTPS configuration
- [ ] **[INFRA-005]** Prometheus metrics
- [ ] **[INFRA-006]** CI/CD pipeline

---

## 📊 RIEPILOGO

| Priorità | Count | Status |
|----------|-------|--------|
| 🔴 Critico | 7 | 0/7 completati |
| ⚠️ Alto | 6 | 0/6 completati |
| 🟡 Medio | 11 | 0/11 completati |
| 🟢 Basso | 8 | 0/8 completati |
| 📋 Pagine | 4 | 0/4 completati |
| 🔧 Infra | 6 | 0/6 completati |
| **TOTALE** | **42** | **0/42** |

---

## 📝 NOTE

- Prioritizzare fix bug critici prima di nuove feature
- Review codice completata il 2025-12-11
- Backend e Frontend entrambi hanno issues da risolvere


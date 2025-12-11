# SunPulse - TODO

> **Last updated:** 2025-12-11  
> **Legend:** 🔴 Critical | ⚠️ High | 🟡 Medium | 🟢 Low

---

## 🔴 CRITICAL BUGS

### Backend

- [ ] **[BE-001]** `useDevices.ts:62` - `stats[device.status]++` invalid in TypeScript
  - File: `modules/frontend/src/hooks/useDevices.ts`
  - Fix: Use correct increment pattern
  
- [ ] **[BE-002]** `data.py:177` - `get_settings()` not imported in try block
  - File: `modules/backend/app/api/v1/endpoints/data.py`
  - Fix: Move import `from ....config.settings import get_settings` to top of file

- [ ] **[BE-003]** `zcs_api_service.py:230` - Chunking uses 23h instead of 24h, may lose data
  - File: `modules/backend/app/services/zcs_api_service.py`
  - Fix: Change `timedelta(hours=23)` to `timedelta(hours=24)`

### Frontend

- [ ] **[FE-001]** `Dashboard.tsx:27-28` - Energy estimate always 0 if `daily_energy=0`
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Add null safety check

- [ ] **[FE-002]** `Dashboard.tsx:133` - Division by zero if `stats.total=0`
  - File: `modules/frontend/src/pages/Dashboard.tsx`
  - Fix: Add guard `stats.total > 0 ? ... : 0`

- [ ] **[FE-003]** `DeviceCard.tsx:128` - Conversion `*1000` kWh→Wh potentially wrong
  - File: `modules/frontend/src/components/devices/DeviceCard.tsx`
  - Fix: Verify ZCS data units and correct

- [ ] **[FE-004]** `PowerChart.tsx:39-87` - Simulated data instead of real
  - File: `modules/frontend/src/components/charts/PowerChart.tsx`
  - Fix: Implement fetch from `/api/v1/data/historical`

---

## ⚠️ ARCHITECTURAL ISSUES

- [ ] **[ARCH-001]** Auth Mock always active
  - File: `modules/frontend/src/providers/AuthProvider.tsx:80`
  - Issue: `isDevelopmentMode = true` hardcoded
  - Fix: Read from env `VITE_AUTH_MOCK=true`

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

- [ ] **[UX-008]** Notification count hardcoded to 3
  - File: `modules/frontend/src/components/layout/Header.tsx:57`
  - Fix: Connect to real notification system

- [ ] **[UX-009]** Quick stats overflow on mobile
  - Fix: Hide header stats on viewport < 768px

### Mobile

- [ ] **[UX-010]** Header stats visible on mobile (clutters UI)
  - Fix: Add `mobile-hidden` class to stats

- [ ] **[UX-011]** Chart slider difficult on touch
  - Fix: Increase touch area or disable on mobile

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

- [ ] **[PAGE-001]** Device Detail Page (`/devices/:id`)
  - Effort: 4h
  
- [ ] **[PAGE-002]** Analytics Page (`/analytics`)
  - Effort: 6h
  
- [ ] **[PAGE-003]** Alarms Page (`/alarms`)
  - Effort: 4h
  
- [ ] **[PAGE-004]** Settings Page (`/settings`)
  - Effort: 3h

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
| 🔴 Critical | 7 | 0/7 completed |
| ⚠️ High | 6 | 0/6 completed |
| 🟡 Medium | 11 | 0/11 completed |
| 🟢 Low | 8 | 0/8 completed |
| 📋 Pages | 4 | 0/4 completed |
| 🔧 Infra | 6 | 0/6 completed |
| **TOTAL** | **42** | **0/42** |

---

## 📝 NOTES

- Prioritize critical bug fixes before new features
- Code review completed on 2025-12-11
- Both backend and frontend have issues to resolve

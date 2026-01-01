# 📖 SunPulse - Manuale Utente

> **Versione**: 1.0  
> **Data**: Dicembre 2025  
> **Autore**: Giovanni Tommasini

---

## 📋 Indice

1. [Introduzione](#introduzione)
2. [Architettura Sistema](#architettura-sistema)
3. [API ZCS Azzurro](#api-zcs-azzurro)
4. [Struttura Dati](#struttura-dati)
5. [Strategia di Caching](#strategia-di-caching)
6. [Guida all'Uso](#guida-alluso)
7. [Lettura Contatore Gas](#lettura-contatore-gas-coming-soon) ⛽ *Coming Soon*
8. [Troubleshooting](#troubleshooting)

---

## 1. Introduzione

**SunPulse** è una dashboard per il monitoraggio di impianti fotovoltaici ZCS Azzurro. Permette di:

- 📊 Visualizzare produzione e consumo in tempo reale
- 📈 Analizzare trend storici
- 🔋 Monitorare stato batteria
- 🚨 Gestire allarmi
- 📧 Ricevere notifiche email

---

## 2. Architettura Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + RefineJS)              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │Dashboard│  │Devices  │  │Analytics│  │ Alarms  │  │Settings│ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬───┘ │
└───────┼────────────┼────────────┼────────────┼────────────┼─────┘
        │            │            │            │            │
        └────────────┴────────────┴────────────┴────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ API Router  │  │ ZCS Service  │  │   Celery Workers        │ │
│  │ /api/v1/*   │  │              │──│ • collect_realtime      │ │
│  └──────┬──────┘  └──────┬───────┘  │ • collect_daily_energy  │ │
│         │                │          │ • collect_alarms        │ │
│         │                │          └───────────┬─────────────┘ │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌──────────────┐  ┌────────────────┐  ┌────────────────────────────┐
│   Redis      │  │ ZCS Azzurro    │  │      PostgreSQL            │
│   (Cache)    │  │ Portal API     │  │  • devices                 │
│              │  │                │  │  • daily_energy            │
│  TTL: 2 min  │  │ Rate Limited   │  │  • alarms                  │
└──────────────┘  └────────────────┘  └────────────────────────────┘
```

---

## 3. API ZCS Azzurro

### 3.1 Configurazione

| Parametro | Valore |
|-----------|--------|
| **Endpoint** | `https://third.zcsazzurroportal.com:19003/` |
| **Metodo** | POST |
| **Authorization** | `Zcs <API_KEY>` |
| **Content-Type** | `application/json` |

### 3.2 Chiamate Disponibili

#### 3.2.1 `realtimeData` - Dati in Tempo Reale

**Scopo**: Ottenere l'ultimo valore di ogni metrica (snapshot attuale)

**Request**:
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

**Response**:
```json
{
  "realtimeData": {
    "success": true,
    "params": {
      "value": [{
        "ZE1ES330J9E558": {
          "lastUpdate": "2025-12-18T22:31:35Z",
          "powerGenerating": 0,
          "powerConsuming": 300,
          "powerImporting": 300,
          "powerExporting": 0,
          "energyGenerating": 5.2,
          "energyConsuming": 24.5,
          "energyGeneratingTotal": 32667,
          "batterySoC": 18,
          ...
        }
      }]
    }
  }
}
```

#### 3.2.2 `historicData` - Dati Storici

**Scopo**: Ottenere serie temporali per grafici (array di valori)

⚠️ **LIMITE**: Massimo 24 ore tra `start` e `end`

**Request**:
```json
{
  "historicData": {
    "command": "historicData",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*",
      "start": "2025-12-18T00:00:00.000Z",
      "end": "2025-12-18T23:59:59.999Z"
    }
  }
}
```

**Response**:
```json
{
  "historicData": {
    "success": true,
    "params": {
      "value": [{
        "ZE1ES330J9E558": {
          "ts": ["2025-12-18T00:00:00Z", "2025-12-18T00:15:00Z", ...],
          "powerGenerating": [0, 0, 50, 200, 500, ...],
          "powerConsuming": [300, 280, 350, ...],
          "energyGeneratingTotalDecimal": [32634.0, 32634.5, 32635.2, ...],
          ...
        }
      }]
    }
  }
}
```

#### 3.2.3 `deviceAlarm` - Allarmi Attuali

**Scopo**: Stato attuale degli allarmi

**Request**:
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

**Response**:
```json
{
  "deviceAlarm": {
    "success": true,
    "params": {
      "value": [{
        "ZE1ES330J9E558": {
          "deviceAlarm": [2, 4],
          "lastUpdate": "2025-12-18T09:32:49Z"
        }
      }]
    }
  }
}
```

#### 3.2.4 `deviceHistoricAlarm` - Storico Allarmi

**Scopo**: Timeline degli allarmi nel tempo

**Request** (max 24 ore):
```json
{
  "deviceHistoricAlarm": {
    "command": "deviceHistoricAlarm",
    "params": {
      "thingKey": "ZE1ES330J9E558",
      "requiredValues": "*",
      "start": "2025-12-18T00:00:00.000Z",
      "end": "2025-12-18T23:59:59.999Z"
    }
  }
}
```

---

## 4. Struttura Dati

### 4.1 Campi Disponibili

#### Potenze Istantanee (W)
| Campo | Descrizione |
|-------|-------------|
| `powerGenerating` | Potenza generata dai pannelli |
| `powerConsuming` | Potenza consumata dalla casa |
| `powerImporting` | Potenza prelevata dalla rete |
| `powerExporting` | Potenza immessa in rete |
| `powerAutoconsuming` | Potenza autoconsumata direttamente |
| `powerCharging` | Potenza di carica batteria |
| `powerDischarging` | Potenza di scarica batteria |

#### Energia Giornaliera (kWh) - Si resetta a mezzanotte
| Campo | Descrizione |
|-------|-------------|
| `energyGenerating` | Energia generata oggi |
| `energyConsuming` | Energia consumata oggi |
| `energyImporting` | Energia prelevata dalla rete oggi |
| `energyExporting` | Energia immessa in rete oggi |
| `energyAutoconsuming` | Autoconsumo oggi |
| `energyCharging` | Carica batteria oggi |
| `energyDischarging` | Scarica batteria oggi |

#### Energia Totale Cumulativa (kWh) - Mai si resetta
| Campo | Descrizione |
|-------|-------------|
| `energyGeneratingTotal` | Totale generato (intero) |
| `energyGeneratingTotalDecimal` | Totale generato (decimale, più preciso) |
| `energyConsumingTotal` | Totale consumato |
| `energyImportingTotal` | Totale da rete |
| `energyExportingTotal` | Totale in rete |
| `energyChargingTotal` | Totale carica batteria |
| `energyDischargingTotal` | Totale scarica batteria |

#### Batteria
| Campo | Descrizione |
|-------|-------------|
| `batterySoC` | Stato di carica (0-100%) |
| `batteryCycletime` | Numero cicli batteria |

#### Altri (solo in historicData)
| Campo | Descrizione |
|-------|-------------|
| `ts` | Array timestamp |
| `currentAC` | Corrente AC |
| `voltageAC` | Tensione AC |
| `frequency` | Frequenza rete (Hz) |
| `temperature` | Temperatura inverter (°C) |

### 4.2 Formule di Calcolo

```
Autoconsumo = Produzione - Immissione in rete
Consumo Totale = Autoconsumo + Prelievo da rete + Scarica batteria
Produzione Netta = Produzione - Carica batteria

Bilancio Energetico:
  Produzione = Autoconsumo + Immissione + Carica Batteria
  Consumo = Autoconsumo + Prelievo + Scarica Batteria
```

---

## 5. Strategia di Caching

### 5.1 Livelli di Cache

| Livello | Storage | TTL | Dati |
|---------|---------|-----|------|
| **L1** | Redis Memory | 2 min | Realtime data |
| **L2** | Redis | 15 min | Historical (ultime 24h) |
| **L3** | PostgreSQL | Forever | Daily aggregates |

### 5.2 Schema Database

```sql
-- Tabella per energia giornaliera aggregata
CREATE TABLE daily_energy (
  id SERIAL PRIMARY KEY,
  device_thing_key VARCHAR(50) NOT NULL,
  date DATE NOT NULL,
  
  -- Produzione (kWh)
  energy_generating DECIMAL(10,2),
  energy_exporting DECIMAL(10,2),
  energy_autoconsuming DECIMAL(10,2),
  
  -- Consumo (kWh)
  energy_consuming DECIMAL(10,2),
  energy_importing DECIMAL(10,2),
  
  -- Batteria (kWh)
  energy_charging DECIMAL(10,2),
  energy_discharging DECIMAL(10,2),
  
  -- Contatori cumulativi (per verifica)
  energy_generating_total DECIMAL(12,2),
  energy_consuming_total DECIMAL(12,2),
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(device_thing_key, date)
);

-- Tabella per storico allarmi
CREATE TABLE alarm_history (
  id SERIAL PRIMARY KEY,
  device_thing_key VARCHAR(50) NOT NULL,
  alarm_codes INTEGER[],
  started_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.3 Task Celery

| Task | Frequenza | Descrizione |
|------|-----------|-------------|
| `collect_realtime` | Ogni 5 min | Aggiorna cache Redis |
| `collect_daily_energy` | Ogni giorno 00:05 | Salva aggregati in PostgreSQL |
| `collect_alarms` | Ogni ora | Controlla nuovi allarmi |
| `cleanup_cache` | Ogni giorno 03:00 | Pulisce cache vecchia |

---

## 6. Guida all'Uso

### 6.1 Dashboard

La dashboard mostra:
- **Produzione Attuale**: Potenza istantanea dai pannelli (W)
- **Energia Prodotta Oggi**: Totale kWh generati oggi
- **Consumo**: Potenza istantanea consumata (W)
- **Stato Batteria**: Percentuale carica

### 6.2 Dispositivi

Lista di tutti gli inverter configurati con:
- Stato online/offline
- Potenza istantanea
- Energia giornaliera
- Accesso al dettaglio

### 6.3 Analytics

Grafici e trend:
- Produzione vs Consumo (ultime 24h, 7gg, 30gg)
- Autoconsumo vs Prelievo rete
- Trend batteria

### 6.4 Impostazioni

- Configurazione notifiche email
- Soglie allarmi
- Preferenze UI

---

## 7. Lettura Contatore Gas (Coming Soon)

### 7.1 Panoramica

SunPulse permette di registrare le letture del contatore gas per monitorare i consumi domestici. Le letture possono essere inserite in due modi:

| Modalità | Descrizione | Quando usarla |
|----------|-------------|---------------|
| **Manuale** | Inserisci il valore letto sul contatore | Sempre affidabile |
| **OCR da Foto** | Scatta una foto al contatore | Più veloce, evita errori di trascrizione |

### 7.2 Inserimento Manuale

1. Vai alla pagina **Contatori** dal menu laterale
2. Clicca su **Nuova Lettura**
3. Seleziona **Gas** come tipo contatore
4. Inserisci il valore letto (es. `12345.678`)
5. Seleziona la data della lettura
6. Aggiungi eventuali note
7. Clicca **Salva**

> ⚠️ **Nota**: Il sistema verifica che la nuova lettura sia maggiore della precedente

### 7.3 Lettura con OCR

1. Vai alla pagina **Contatori**
2. Clicca su **Scatta Foto** o **Carica Immagine**
3. Inquadra il display del contatore
4. Il sistema riconosce automaticamente le cifre
5. Verifica il valore rilevato e conferma
6. Se necessario, correggi manualmente

**Suggerimenti per foto migliori:**
- 📷 Buona illuminazione (no riflessi)
- 🔍 Inquadratura frontale del display
- 📏 Avvicinati per vedere bene le cifre
- 🧹 Pulisci il vetro del contatore se sporco

### 7.4 Storico e Consumi

Nella sezione **Storico Letture** puoi:
- 📊 Vedere il grafico dei consumi nel tempo
- 📋 Consultare la tabella delle letture
- 📈 Calcolare il consumo tra due date
- 📥 Esportare i dati in CSV

### 7.5 Calcolo Consumo

Il consumo viene calcolato automaticamente:

```
Consumo = Lettura Attuale - Lettura Precedente
```

Esempio:
- Lettura 1 Dicembre: 12.345 m³
- Lettura 1 Gennaio: 12.489 m³
- **Consumo Dicembre**: 144 m³ (12.489 - 12.345)

---

## 8. Troubleshooting

### 8.1 Dati a 0

**Problema**: I valori di energia giornaliera sono 0

**Cause possibili**:
1. È notte e non c'è produzione
2. I dati si resettano a mezzanotte (timezone ZCS)
3. Cache non aggiornata

**Soluzione**: Il sistema usa i contatori cumulativi (`*TotalDecimal`) per calcolare l'energia giornaliera in modo più preciso.

### 8.2 Disconnesso

**Problema**: La dashboard mostra "Disconnesso"

**Cause possibili**:
1. WebSocket disabilitato (normale in modalità polling)
2. Backend non raggiungibile
3. Problemi di rete

**Soluzione**: Verificare che il backend sia attivo e raggiungibile.

### 8.3 Errore 400/500

**Problema**: Errori nelle chiamate API

**Cause possibili**:
1. API ZCS non raggiungibile
2. Credenziali scadute
3. Rate limiting

**Soluzione**: Controllare i log del backend (`docker logs sunpulse_backend`).

---

## 📞 Supporto

- **Repository**: https://github.com/giovannitommasini/sunpulse
- **Autore**: Giovanni Tommasini
- **Email**: tommasini.giovanni@gmail.com

---

*Made with ☀️ by Giovanni Tommasini - © 2025 SunPulse*

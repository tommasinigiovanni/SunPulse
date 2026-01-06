# 🗺️ Google Maps API - Setup e Configurazione

> **Creato:** 2026-01-06  
> **Scopo:** Documentare la configurazione delle Google Maps API per la funzionalità Building Address Autocomplete

---

## 📋 Panoramica

SunPulse utilizza le Google Maps API per:
- **Places Autocomplete**: ricerca indirizzi durante la creazione edifici
- **Geocoding**: conversione indirizzo → coordinate GPS (lat/lng)
- **Timezone API**: rilevamento automatico timezone da coordinate

---

## 🔑 Ottenere API Key

### 1. Creare Progetto Google Cloud

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Nome suggerito: `sunpulse-production`

### 2. Abilitare API Necessarie

Nel progetto, abilita le seguenti API:

| API | Descrizione | Costo Stimato |
|-----|-------------|---------------|
| **Places API** | Autocomplete indirizzi | ~€17/1000 richieste |
| **Geocoding API** | Indirizzo → coordinate | ~€5/1000 richieste |
| **Time Zone API** | Coordinate → timezone | ~€5/1000 richieste |
| **Maps JavaScript API** | Mappa interattiva (frontend) | Gratuito fino a 28.000 caricamenti/mese |

### 3. Creare API Key

1. Vai su **API e servizi** → **Credenziali**
2. Clicca **+ CREA CREDENZIALI** → **Chiave API**
3. Copia la chiave generata

### 4. Configurare Restrizioni (IMPORTANTE!)

Per sicurezza, configura restrizioni sulla chiave:

#### Backend Key (per server-side)
```
Tipo: Restrizioni IP
IP consentiti: 
  - IP del server di produzione
  - 127.0.0.1 (per sviluppo locale)

API consentite:
  - Places API
  - Geocoding API
  - Time Zone API
```

#### Frontend Key (per client-side)
```
Tipo: Restrizioni HTTP referrer
Referrer consentiti:
  - https://yourdomain.com/*
  - http://localhost:3000/* (per sviluppo)

API consentite:
  - Maps JavaScript API
  - Places API (solo Autocomplete)
```

> ⚠️ **Nota**: È consigliato usare **2 chiavi separate** (una per backend, una per frontend)

---

## ⚙️ Configurazione Applicazione

### Backend (.env)

Aggiungi al file `.env` del backend:

```bash
# Google APIs
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Frontend (.env)

Aggiungi al file `.env` del frontend:

```bash
# Google Maps API (per Address Autocomplete)
VITE_GOOGLE_MAPS_API_KEY=AIzaSyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

### Verifica Configurazione

Il file `index.html` carica automaticamente lo script Google Maps:

```html
<script>
  (function() {
    const apiKey = import.meta.env?.VITE_GOOGLE_MAPS_API_KEY;
    if (apiKey && apiKey !== 'your-google-maps-api-key') {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&language=it`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    }
  })();
</script>
```

---

## 💰 Costi Stimati

### Scenario: 100 utenti attivi

| Operazione | Frequenza | Richieste/mese | Costo/mese |
|------------|-----------|----------------|------------|
| Autocomplete indirizzo | 1 per nuovo edificio | ~100 | €1.70 |
| Geocoding | 1 per nuovo edificio | ~100 | €0.50 |
| Timezone | 1 per nuovo edificio | ~100 | €0.50 |
| **TOTALE** | | **~300** | **~€2.70** |

### Free Tier Google Maps

Google offre **$200 di credito mensile gratuito**, che copre:
- ~11.700 richieste Autocomplete
- ~40.000 richieste Geocoding
- ~40.000 richieste Timezone

> ✅ **Per la maggior parte dei casi d'uso, l'utilizzo rientra nel free tier!**

---

## 🧪 Test Configurazione

### Test Backend (Python)

```python
import googlemaps
import os

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Test Geocoding
result = gmaps.geocode('Via Roma 1, Milano')
print(f"Coordinate: {result[0]['geometry']['location']}")

# Test Timezone
import datetime
timezone = gmaps.timezone(
    location=(45.4642, 9.1900),
    timestamp=datetime.datetime.now()
)
print(f"Timezone: {timezone['timeZoneId']}")
```

### Test Frontend (Browser Console)

```javascript
// Verifica che lo script sia caricato
console.log('Google Maps loaded:', typeof google !== 'undefined');

// Test Autocomplete
const service = new google.maps.places.AutocompleteService();
service.getPlacePredictions(
  { input: 'Via Roma, Milano' },
  (predictions, status) => {
    console.log('Predictions:', predictions);
  }
);
```

---

## 🔒 Sicurezza

### Best Practices

1. **Mai committare API key nel codice**
   - Usa sempre variabili ambiente
   - Aggiungi `.env` al `.gitignore`

2. **Usa restrizioni appropriate**
   - IP per backend
   - HTTP referrer per frontend

3. **Monitora utilizzo**
   - Configura alert su Google Cloud Console
   - Imposta budget limit (es: €10/mese)

4. **Ruota le chiavi periodicamente**
   - Ogni 6-12 mesi
   - Immediatamente se compromesse

---

## 🐛 Troubleshooting

### Errore: "This API project is not authorized to use this API"

**Soluzione**: Abilita l'API nel progetto Google Cloud

```bash
# Vai su Google Cloud Console
# → API e servizi → Libreria
# → Cerca "Places API" → Abilita
```

### Errore: "API key not valid"

**Soluzione**: Verifica restrizioni API key

1. Controlla che l'IP/referrer sia consentito
2. Verifica che l'API sia abilitata per quella chiave

### Errore: "REQUEST_DENIED"

**Soluzione**: Controlla fatturazione

1. Vai su **Fatturazione** in Google Cloud Console
2. Assicurati che il progetto abbia un metodo di pagamento valido

---

## 📚 Riferimenti

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Places API Autocomplete](https://developers.google.com/maps/documentation/places/web-service/autocomplete)
- [Geocoding API](https://developers.google.com/maps/documentation/geocoding)
- [Time Zone API](https://developers.google.com/maps/documentation/timezone)
- [Pricing Calculator](https://mapsplatform.google.com/pricing/)

---

## ✅ Checklist Setup

- [ ] Progetto Google Cloud creato
- [ ] Places API abilitata
- [ ] Geocoding API abilitata
- [ ] Time Zone API abilitata
- [ ] Maps JavaScript API abilitata
- [ ] API key backend creata con restrizioni IP
- [ ] API key frontend creata con restrizioni referrer
- [ ] Chiavi aggiunte ai file `.env`
- [ ] Test backend eseguito con successo
- [ ] Test frontend eseguito con successo
- [ ] Alert budget configurato
- [ ] Documentazione team aggiornata

---

*Ultimo aggiornamento: 2026-01-06*


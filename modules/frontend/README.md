# SunPulse Frontend

Dashboard moderna e responsive per il monitoraggio di impianti fotovoltaici in tempo reale, costruita con React, RefineJS e Auth0.

## 🚀 Caratteristiche

- **Autenticazione sicura** con Auth0
- **Dashboard real-time** con WebSocket e fallback polling
- **Gestione dispositivi** con visualizzazione stato e metriche
- **Grafici interattivi** per produzione vs consumo
- **Design responsive** ottimizzato per mobile e desktop
- **Gestione errori** robusta con Error Boundaries
- **TypeScript** per type safety completa
- **Testing** con Jest e React Testing Library

## 🛠️ Stack Tecnologico

- **Framework**: React 18 + TypeScript
- **UI Library**: Ant Design + RefineJS
- **Autenticazione**: Auth0
- **State Management**: TanStack Query (React Query)
- **Charts**: Ant Design Charts
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Testing**: Jest + React Testing Library

## 📦 Installazione

1. **Installa le dipendenze:**
   ```bash
   npm install
   ```

2. **Configura le variabili d'ambiente:**
   ```bash
   cp env.example .env.local
   ```
   
   Modifica `.env.local` con i tuoi valori:
   ```env
   REACT_APP_API_URL=http://localhost:8000/api/v1
   REACT_APP_WS_URL=ws://localhost:8000/ws
   REACT_APP_AUTH0_DOMAIN=your-domain.auth0.com
   REACT_APP_AUTH0_CLIENT_ID=your-client-id
   REACT_APP_AUTH0_AUDIENCE=https://sunpulse-api
   ```

3. **Avvia il server di sviluppo:**
   ```bash
   npm run dev
   ```

4. **Apri il browser:**
   ```
   http://localhost:3000
   ```

## 🔧 Configurazione Auth0

### 1. Crea un'applicazione Auth0

1. Vai su [Auth0 Dashboard](https://manage.auth0.com)
2. Crea una nuova applicazione di tipo "Single Page Application"
3. Configura gli URL:
   - **Allowed Callback URLs**: `http://localhost:3000`
   - **Allowed Logout URLs**: `http://localhost:3000`
   - **Allowed Web Origins**: `http://localhost:3000`

### 2. Configura API e Permissions

Crea un'API con i seguenti scope:
- `read:devices` - Lettura dispositivi
- `write:devices` - Gestione dispositivi
- `read:analytics` - Visualizzazione analytics
- `admin` - Accesso amministrativo

### 3. Configura Roles e Rules

Crea rules per assegnare ruoli e permessi agli utenti:

```javascript
function (user, context, callback) {
  const namespace = 'https://sunpulse-app/';
  const assignedRoles = (context.authorization || {}).roles;
  
  let idTokenClaims = context.idToken || {};
  let accessTokenClaims = context.accessToken || {};
  
  idTokenClaims[`${namespace}roles`] = assignedRoles;
  accessTokenClaims[`${namespace}roles`] = assignedRoles;
  
  // Assegna permessi base per tutti gli utenti
  const permissions = ['read:devices'];
  
  // Aggiungi permessi per admin
  if (assignedRoles && assignedRoles.includes('admin')) {
    permissions.push('write:devices', 'read:analytics', 'admin');
  }
  
  idTokenClaims[`${namespace}permissions`] = permissions;
  accessTokenClaims[`${namespace}permissions`] = permissions;
  
  context.idToken = idTokenClaims;
  context.accessToken = accessTokenClaims;
  
  callback(null, user, context);
}
```

## 🏗️ Struttura del Progetto

```
src/
├── components/           # Componenti riutilizzabili
│   ├── common/          # Componenti comuni (ProtectedRoute, etc.)
│   ├── layout/          # Layout components (Header, Sidebar)
│   ├── charts/          # Grafici e visualizzazioni
│   ├── devices/         # Componenti per gestione dispositivi
│   └── alerts/          # Sistema notifiche e allarmi
├── pages/               # Pagine principali
│   ├── Dashboard.tsx    # Dashboard principale
│   ├── Devices.tsx      # Gestione dispositivi
│   ├── Analytics.tsx    # Analytics avanzate
│   └── Settings.tsx     # Impostazioni
├── hooks/               # Custom hooks
│   ├── useAuth.ts       # Hook autenticazione
│   ├── useRealTimeData.ts # Hook dati real-time
│   ├── useDevices.ts    # Hook gestione dispositivi
│   └── useWebSocket.ts  # Hook WebSocket generico
├── providers/           # Context providers
│   ├── AuthProvider.tsx # Provider Auth0
│   └── DataProvider.ts  # Provider dati Refine
├── types/               # Type definitions
│   ├── device.ts        # Tipi dispositivi
│   ├── alarm.ts         # Tipi allarmi
│   └── api.ts          # Tipi API
├── utils/               # Utilities
│   ├── api.ts          # Client API e interceptors
│   ├── formatters.ts   # Funzioni formattazione
│   └── constants.ts    # Costanti applicazione
└── styles/             # Stili globali
    └── global.css      # CSS globale e utilities
```

## 🎨 Componenti Principali

### Dashboard
- **KPI Cards**: Metriche real-time (produzione, consumo, risparmio)
- **PowerChart**: Grafico produzione vs consumo con dati storici
- **DeviceList**: Lista dispositivi con stato e metriche
- **Analytics**: Statistiche avanzate e proiezioni

### Gestione Dispositivi
- **DeviceCard**: Card singolo dispositivo con metriche
- **DeviceList**: Lista/griglia dispositivi con filtri
- **DeviceDetail**: Pagina dettaglio dispositivo
- **DeviceFilters**: Sistema filtri avanzati

### Real-time Features
- **WebSocket Connection**: Aggiornamenti live via WebSocket
- **Fallback Polling**: Polling automatico se WebSocket non disponibile
- **Connection Status**: Indicatore stato connessione
- **Auto Reconnection**: Riconnessione automatica

## 🔄 Gestione Stato

### TanStack Query
- Cache intelligente per dati API
- Invalidazione automatica
- Retry logic configurabile
- Background updates

### WebSocket State
- Gestione connessione WebSocket
- Buffer messaggi durante disconnessione
- Heartbeat per mantenere connessione
- Gestione errori e riconnessione

## 📱 Responsive Design

- **Mobile First**: Design ottimizzato per mobile
- **Breakpoints**: 
  - XS: < 576px (mobile)
  - SM: 576px - 768px (tablet)
  - MD: 768px - 992px (desktop small)
  - LG: 992px+ (desktop)
- **Adaptive Layout**: Layout che si adatta al dispositivo
- **Touch Friendly**: Interfaccia ottimizzata per touch

## 🧪 Testing

### Esegui i test
```bash
# Test singolo
npm test

# Test in modalità watch
npm run test:watch

# Coverage report
npm test -- --coverage
```

### Struttura Test
```
src/
├── components/
│   └── __tests__/
│       ├── DeviceCard.test.tsx
│       ├── PowerChart.test.tsx
│       └── Dashboard.test.tsx
├── hooks/
│   └── __tests__/
│       ├── useAuth.test.ts
│       └── useDevices.test.ts
└── utils/
    └── __tests__/
        ├── formatters.test.ts
        └── api.test.ts
```

## 📈 Performance

### Ottimizzazioni Implementate
- **Code Splitting**: Lazy loading delle route
- **Memoization**: React.memo per componenti pesanti
- **Virtual Scrolling**: Per liste grandi
- **Image Optimization**: Lazy loading immagini
- **Bundle Analysis**: Analisi dimensioni bundle

### Metriche Target
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## 🔒 Sicurezza

### Misure Implementate
- **CSP Headers**: Content Security Policy
- **Auth Token Security**: Token sicuri in memoria
- **Input Validation**: Validazione client-side
- **Error Boundaries**: Gestione errori sicura
- **Dependencies Security**: Audit regolari

### Best Practices
- Token refresh automatico
- Logout automatico su token scaduto
- Sanitizzazione input utente
- Gestione errori senza leak informazioni

## 🚀 Build e Deploy

### Build di produzione
```bash
# Build ottimizzato
npm run build

# Preview build locale
npm run preview

# Analisi bundle
npm run build-analyze
```

### Docker
```bash
# Build immagine
docker build -t sunpulse-frontend .

# Run container
docker run -p 3000:80 sunpulse-frontend
```

### Deploy su Nginx
Il build genera file statici in `dist/` pronti per essere serviti da Nginx.

## 🐛 Troubleshooting

### Auth0 Issues
```bash
# Verifica configurazione
console.log('Auth0 Domain:', process.env.REACT_APP_AUTH0_DOMAIN)
console.log('Auth0 Client ID:', process.env.REACT_APP_AUTH0_CLIENT_ID)
```

### WebSocket Issues
```bash
# Test connessione WebSocket
wscat -c ws://localhost:8000/ws
```

### API Issues
```bash
# Test health check API
curl http://localhost:8000/api/v1/health
```

## 📚 Risorse Utili

- [RefineJS Documentation](https://refine.dev/)
- [Ant Design Components](https://ant.design/components/overview/)
- [Auth0 React SDK](https://auth0.com/docs/quickstart/spa/react)
- [TanStack Query](https://tanstack.com/query/latest)
- [React Router v6](https://reactrouter.com/en/main)

## 🤝 Contribuzioni

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è licenziato sotto la licenza MIT - vedi il file [LICENSE](LICENSE) per i dettagli. 
# 📖 SunPulse - Manuale Utente

> **Versione**: 2.2.0
> **Data**: Gennaio 2026
> **Ultimo aggiornamento**: 2026-01-03

---

## 📋 Indice

1. [Introduzione](#1-introduzione)
2. [Accesso alla Piattaforma](#2-accesso-alla-piattaforma)
3. [**Gestione Edifici**](#3-gestione-edifici) 🏢 *NUOVO*
4. [Dashboard Principale](#4-dashboard-principale)
5. [Gestione Dispositivi](#5-gestione-dispositivi)
6. [Analytics e Analisi](#6-analytics-e-analisi)
7. [Allarmi e Notifiche](#7-allarmi-e-notifiche)
8. [Impostazioni](#8-impostazioni)
9. [Lettura Contatore Gas](#9-lettura-contatore-gas) ⛽ *Coming Soon*
10. [Architettura Tecnica](#10-architettura-tecnica)
11. [API ZCS Azzurro](#11-api-zcs-azzurro)
12. [Troubleshooting](#12-troubleshooting)
13. [FAQ](#13-faq)

---

## 1. Introduzione

### 1.1 Cos'è SunPulse?

**SunPulse** è una piattaforma web completa per il monitoraggio e la gestione di impianti fotovoltaici con sistemi di accumulo ZCS Azzurro. Offre un'interfaccia intuitiva per controllare in tempo reale la produzione di energia solare e ottimizzare i consumi domestici.

### 1.2 Funzionalità Principali

- ⚡ **Monitoraggio Real-Time**: Visualizzazione istantanea di produzione, consumo e stato batteria
- 📊 **Dashboard Interattiva**: Grafici e statistiche per comprendere il bilancio energetico
- 📈 **Analytics Avanzate**: Analisi storiche con confronto produzione vs consumo
- 🔋 **Gestione Batteria**: Monitoraggio stato di carica e cicli batteria
- 🚨 **Sistema Allarmi**: Notifiche immediate per anomalie e manutenzione
- 📧 **Email Notifications**: Report giornalieri e alert automatici
- 💰 **Calcolo Risparmi**: Stima risparmi economici e CO₂ evitata
- 🔧 **Multi-Dispositivo**: Supporto per più inverter e gestione centralizzata

### 1.3 Requisiti di Sistema

**Browser Supportati:**
- Chrome/Edge (versione 90+)
- Firefox (versione 88+)
- Safari (versione 14+)

**Dispositivi Compatibili:**
- Desktop (Windows, macOS, Linux)
- Tablet (iPad, Android)
- Smartphone (iOS, Android)

**Connessione Internet:**
- Minimo 2 Mbps per visualizzazione grafici

---

## 2. Accesso alla Piattaforma

### 2.1 Login

1. Apri il browser e vai all'indirizzo: `https://sunpulse.your-domain.com`
2. Vedrai la pagina di login con il logo SunPulse
3. Clicca su **"Accedi con Auth0"**
4. Inserisci le tue credenziali (email e password)
5. Al primo accesso, ti verrà chiesto di verificare l'email

> **Nota**: SunPulse utilizza Auth0 per garantire la massima sicurezza. Le tue credenziali sono protette con crittografia end-to-end.

### 2.2 Navigazione

Dopo il login, vedrai il menu laterale con le seguenti sezioni:

| Sezione | Icona | Descrizione |
|---------|-------|-------------|
| **Dashboard** | 📊 | Panoramica generale del sistema |
| **Dispositivi** | ⚡ | Lista e dettaglio dispositivi |
| **Analytics** | 📈 | Analisi storiche e trend |
| **Allarmi** | 🔔 | Gestione notifiche e alert |
| **Impostazioni** | ⚙️ | Configurazione sistema |

### 2.3 Aggiornamento Dati

I dati vengono aggiornati automaticamente:
- **Dati Real-Time**: ogni 2 minuti
- **Grafici Dashboard**: aggiornamento automatico ogni 5 minuti
- **Dati Storici**: salvati nel database ogni giorno a mezzanotte
- **Dati Meteo**: ogni 15 minuti per ogni edificio

Puoi forzare l'aggiornamento cliccando sul pulsante **"Aggiorna"** nelle varie pagine.

---

## 3. Gestione Edifici 🏢

> **Concetto Chiave**: L'edificio è l'entità centrale di SunPulse. Prima di poter monitorare i tuoi dispositivi, devi creare almeno un edificio.

### 3.1 Cos'è un Edificio?

In SunPulse, un **Edificio** rappresenta una location fisica (casa, ufficio, capannone, ecc.) dove sono installati i dispositivi fotovoltaici. Ogni edificio ha:

- **Nome**: Un nome identificativo (es: "Casa Principale", "Ufficio Milano")
- **Indirizzo**: L'indirizzo completo con ricerca automatica Google
- **Coordinate GPS**: Determinate automaticamente dall'indirizzo
- **Dati Meteo**: Temperatura e condizioni meteo in tempo reale
- **Dispositivi**: Gli inverter e le batterie associati

### 3.2 Primo Accesso: Creazione Edificio

Al primo accesso, se non hai ancora edifici configurati, vedrai la schermata di **Onboarding**:

1. Clicca su **"Crea il tuo primo edificio"**
2. Inserisci il **Nome** dell'edificio (es: "Casa Vacanze Rimini")
3. Inizia a digitare l'**Indirizzo** nel campo di ricerca
4. Seleziona l'indirizzo corretto dalla lista di suggerimenti (Google Places)
5. Verifica la posizione sulla mappa di anteprima
6. Clicca su **"Crea Edificio"**

> **Nota**: L'indirizzo viene ricercato in tempo reale tramite Google Places Autocomplete. Inizia a digitare e seleziona il risultato corretto dalla lista.

### 3.3 Servizio Temperatura

Quando crei un edificio, viene attivato automaticamente un servizio che:

- Recupera la temperatura attuale ogni 15 minuti
- Mostra le condizioni meteo (sole, nuvole, pioggia, ecc.)
- Visualizza orari di alba e tramonto
- Permette di correlare la produzione fotovoltaica con il meteo

Questi dati sono visibili:
- Nel selettore edificio nell'Header (icona meteo + temperatura)
- Nella Dashboard principale
- Nella pagina dettaglio edificio

### 3.4 Gestione Multipla Edifici

Puoi creare e gestire più edifici. Casi d'uso comuni:
- Casa principale + Casa vacanze
- Edificio residenziale + Ufficio
- Più unità immobiliari

**Per aggiungere un nuovo edificio:**
1. Clicca sul selettore edificio nell'Header
2. Seleziona **"+ Aggiungi Edificio"**
3. Compila il form come al primo accesso

**Per cambiare edificio attivo:**
1. Clicca sul selettore edificio nell'Header
2. Seleziona l'edificio desiderato dalla lista
3. La Dashboard e tutti i dati si aggiorneranno per mostrare l'edificio selezionato

### 3.5 Condivisione Edificio

Più utenti possono accedere allo stesso edificio. Questo è utile per:
- Famiglie che vogliono monitorare lo stesso impianto
- Installatori che devono accedere per manutenzione
- Amministratori di condominio

**Ruoli disponibili:**

| Ruolo | Permessi |
|-------|----------|
| **Owner** | Controllo completo, può eliminare l'edificio |
| **Admin** | Può gestire dispositivi e invitare membri |
| **Member** | Può visualizzare dati e ricevere notifiche |
| **Viewer** | Solo visualizzazione, accesso read-only |

**Per invitare un utente:**
1. Vai su **Impostazioni → Edifici** o nella pagina dettaglio edificio
2. Clicca su **"Gestisci Membri"**
3. Inserisci l'email dell'utente da invitare
4. Seleziona il ruolo
5. Clicca su **"Invia Invito"**

L'utente invitato riceverà un'email con il link per accettare l'invito.

### 3.6 Associazione Dispositivi

Dopo aver creato l'edificio, devi associare i dispositivi ZCS:

1. Vai nella pagina **Dispositivi** o **Impostazioni → Edifici → [Edificio] → Dispositivi**
2. Clicca su **"Associa Dispositivo"**
3. Inserisci la **Thing Key** del dispositivo ZCS (es: `ZE1ES330J9E558`)
4. Assegna un nome identificativo (es: "Inverter Tetto Sud")
5. Clicca su **"Associa"**

Il dispositivo verrà collegato all'edificio e inizierà la raccolta dati.

### 3.7 Modifica ed Eliminazione Edificio

**Per modificare un edificio:**
1. Vai su **Impostazioni → Edifici**
2. Clicca sull'icona ✏️ accanto all'edificio
3. Modifica nome o indirizzo
4. Clicca su **"Salva"**

**Per eliminare un edificio:**
1. Vai su **Impostazioni → Edifici**
2. Clicca sull'icona 🗑️ accanto all'edificio
3. Conferma l'eliminazione

> ⚠️ **Attenzione**: L'eliminazione di un edificio rimuoverà anche tutti i dispositivi associati e i relativi dati storici. Questa azione non è reversibile.

---

## 4. Dashboard Principale

La Dashboard è la pagina principale che mostra una panoramica completa del tuo impianto fotovoltaico.

### 4.1 Selettore Edificio e Dispositivo

In alto trovi due selettori:

**🏢 Selettore Edificio** (nell'Header):
- Mostra l'edificio attualmente selezionato
- Visualizza la temperatura attuale dell'edificio
- Clicca per cambiare edificio o crearne uno nuovo

**⚡ Selettore Dispositivo** (nella Dashboard):
- Visualizzare dati aggregati di tutti i dispositivi (opzione predefinita: "🏠 Tutti i dispositivi")
- Filtrare i dati per un singolo inverter (es: "⚡ Inverter ZCS 1")

### 4.2 KPI Cards (Indicatori Principali)

Quattro card mostrano le metriche più importanti:

#### ⚡ Produzione Attuale
- **Valore**: Potenza istantanea generata dai pannelli (in W o kW)
- **Colore**: Blu
- **Info**: Mostra la percentuale di variazione rispetto alla media

#### ✅ Energia Prodotta Oggi
- **Valore**: Totale kWh generati dall'inizio della giornata
- **Colore**: Verde
- **Info**: Si resetta a mezzanotte

#### 💰 Risparmio Oggi
- **Valore**: Risparmio economico stimato in euro (€)
- **Colore**: Arancione
- **Calcolo**: Energia autoconsumata × €0,25/kWh

#### 🌱 CO₂ Risparmiata
- **Valore**: Chilogrammi di CO₂ evitati
- **Colore**: Verde
- **Calcolo**: Energia prodotta × 0,4 kg CO₂/kWh

### 4.3 Bilancio Energetico Giornaliero

Tre card mostrano la suddivisione dettagliata di produzione e consumo:

#### 💡 Consumo Giornaliero
Mostra da dove proviene l'energia che stai consumando:
- **☀️ Dal Sole** (autoconsumo diretto): Energia usata mentre i pannelli producono
- **🔌 Dalla Rete**: Energia prelevata quando la produzione non basta
- **🔋 Dalla Batteria**: Energia scaricata dall'accumulo (se presente)

#### ⚡ Produzione Giornaliera
Mostra come viene utilizzata l'energia prodotta:
- **🏠 Autoconsumo**: Energia usata direttamente in casa
- **⚡ Immesso in Rete**: Energia in eccesso venduta al gestore
- **🔋 Verso Batteria**: Energia utilizzata per caricare l'accumulo

#### ☁️ Potenza Istantanea
Valori in tempo reale:
- **Produzione**: kW generati ora
- **Consumo**: kW consumati ora
- **Dalla Rete**: kW prelevati ora
- **In Rete**: kW immessi ora
- **🔋 Batteria**: Percentuale di carica con barra di progresso colorata
- **🌡️ Temperatura**: Temperatura attuale dell'edificio (dal servizio meteo)

### 4.4 Grafico Produzione vs Consumo

Grafico a linee che mostra l'andamento nelle ultime 24 ore:
- **Linea Verde**: Produzione fotovoltaica
- **Linea Arancione**: Consumo domestico
- **Area Verde**: Autoconsumo (quando produzione > consumo)
- **Area Grigia**: Prelievo da rete (quando consumo > produzione)

**Interattività:**
- Passa il mouse per vedere i valori precisi
- Lo zoom può essere attivato selezionando un'area
- Il grafico si aggiorna automaticamente ogni 5 minuti

### 4.5 Analytics Avanzate

Card finale con stime annuali:
- **Produzione Annuale Stimata**: Basata sulla media giornaliera
- **Risparmio Annuale Stimato**: In euro (€)
- **CO₂ Risparmiata Annuale**: In kg
- **Alberi Equivalenti**: CO₂ risparmiata convertita in alberi piantati (1 albero assorbe ~20 kg CO₂/anno)

---

## 5. Gestione Dispositivi

### 5.1 Lista Dispositivi

Dalla pagina **Dispositivi** puoi vedere tutti gli inverter e i sistemi di accumulo configurati.

**Informazioni Visualizzate:**
- Nome dispositivo (es: "Inverter ZCS 1")
- Thing Key (codice identificativo ZCS)
- Stato: 🟢 Online | 🔴 Offline | 🟡 Warning | 🔧 Manutenzione
- Potenza istantanea attuale
- Energia prodotta oggi
- Ultimo aggiornamento dati

**Azioni Disponibili:**
- **Clicca sulla card** per aprire i dettagli completi
- **Aggiorna**: Forza il refresh dei dati

> **Nota**: I dispositivi mostrati appartengono all'edificio attualmente selezionato. Per vedere i dispositivi di un altro edificio, cambia l'edificio dal selettore nell'Header.

### 5.2 Dettaglio Dispositivo

Cliccando su un dispositivo accedi alla **pagina di dettaglio** con:

#### KPI Principali
- ⚡ **Potenza Attuale**: Produzione istantanea (W/kW)
- ✅ **Energia Prodotta Oggi**: Totale giornaliero (kWh)
- 📉 **Consumo**: Potenza consumata (W/kW)
- 🔋 **Stato Batteria**: Percentuale di carica + barra progresso

#### Bilancio Energetico Dettagliato

**🔋 Produzione Oggi:**
- ☀️ Energia Generata
- ⚡ Immesso in Rete
- 🔋 Caricato in Batteria
- 🏠 Autoconsumo

**🏠 Consumo Oggi:**
- ⚡ Consumo Totale
- ☀️ Dal Sole (autoconsumo)
- 🔋 Dalla Batteria
- 🔌 Dalla Rete

#### Grafico Storico
Produzione vs Consumo delle ultime 24 ore per il dispositivo specifico.

#### Dati Real-Time
Dettagli tecnici istantanei:
- Potenza Generazione / Consumo
- Potenza Importazione / Esportazione
- Potenza Carica / Scarica Batteria

#### Totali Storici
Contatori cumulativi dall'installazione:
- Energia Generata Totale (MWh)
- Energia Consumata Totale (MWh)
- Energia Importata/Esportata Totale (MWh)
- Cicli Batteria
- Ultimo Aggiornamento

**Pulsanti Azione:**
- **← Torna ai dispositivi**: Ritorna alla lista
- **🔄 Aggiorna**: Ricarica i dati
- **⚙️ Configura**: (Funzione riservata all'amministratore)

---

## 6. Analytics e Analisi

La pagina **Analytics** offre strumenti avanzati per analizzare i dati storici e ottimizzare i consumi.

### 6.1 Selettore Periodo

Scegli l'intervallo temporale da analizzare:
- **Oggi**: Dati della giornata corrente
- **Settimana**: Ultimi 7 giorni
- **Mese**: Ultimi 30 giorni
- **Anno**: Ultimi 12 mesi

### 6.2 KPI Analytics

Quattro indicatori mostrano i totali aggregati per il periodo selezionato:

#### ⚡ Produzione
- Totale energia generata nel periodo (kWh)
- Colore: Verde

#### 📉 Consumo
- Totale energia consumata nel periodo (kWh)
- Colore: Arancione

#### 💰 Risparmio
- Risparmio economico totale (€)
- **Autoconsumo**: Energia autoconsumata × €0,25/kWh
- **Vendita**: Energia immessa in rete × €0,10/kWh

#### 🌱 CO₂ Risparmiata
- CO₂ evitata grazie alla produzione solare (kg)
- Calcolo: Produzione × 0,4 kg CO₂/kWh

### 6.3 Indicatori di Performance

#### 📊 Tasso di Autoconsumo
Percentuale di energia prodotta che viene utilizzata direttamente in casa (senza passare per la rete).

**Formula:**
```
Autoconsumo (%) = (Energia Autoconsumata / Energia Prodotta) × 100
```

**Valori Ottimali:**
- **> 70%**: Eccellente - stai usando la maggior parte dell'energia prodotta
- **50-70%**: Buono - sistema ben bilanciato
- **< 50%**: Da migliorare - considera l'installazione di batterie

#### 🏠 Tasso di Autosufficienza
Percentuale del consumo domestico coperta da fonti proprie (solare + batteria).

**Formula:**
```
Autosufficienza (%) = ((Autoconsumo + Da Batteria) / Consumo Totale) × 100
```

**Valori Ottimali:**
- **> 80%**: Eccellente - quasi indipendente dalla rete
- **60-80%**: Buono - buona autonomia energetica
- **< 60%**: Da migliorare - dipendi ancora molto dalla rete

### 6.4 Grafico Produzione vs Consumo

Grafico a barre raggruppate che mostra:
- **Barre Verdi**: Produzione giornaliera
- **Barre Arancioni**: Consumo giornaliero

**Come leggerlo:**
- Quando la barra verde è più alta: hai prodotto più di quanto consumato (surplus)
- Quando la barra arancione è più alta: hai consumato più di quanto prodotto (deficit)

### 6.5 Grafici a Torta

Due grafici circolari mostrano la distribuzione energetica:

#### 🔋 Distribuzione Consumo
Mostra da dove proviene l'energia consumata:
- **Dal Sole** (verde): Autoconsumo diretto
- **Dalla Batteria** (viola): Energia accumulata
- **Dalla Rete** (blu): Prelievo dal gestore

#### ⚡ Distribuzione Produzione
Mostra come viene utilizzata l'energia prodotta:
- **Autoconsumo** (verde): Usata in casa
- **Verso Batteria** (viola): Per accumulo
- **Verso Rete** (blu): Venduta al gestore

### 6.6 Tabelle Riepilogo

Due tabelle dettagliate mostrano i valori numerici esatti:

**⚡ Riepilogo Produzione:**
- Energia Generata
- Autoconsumo
- Verso Batteria
- Immesso in Rete

**🏠 Riepilogo Consumo:**
- Consumo Totale
- Dal Sole
- Dalla Batteria
- Dalla Rete

---

## 7. Allarmi e Notifiche

La pagina **Allarmi** permette di monitorare e gestire tutte le notifiche e gli alert del sistema.

### 7.1 Dashboard Allarmi

In alto vengono mostrati 4 contatori:

| Indicatore | Descrizione | Colore |
|------------|-------------|--------|
| **Allarmi Attivi** | Numero di allarmi che richiedono attenzione | Rosso |
| **In Attesa** | Allarmi presi in carico ma non ancora risolti | Arancione |
| **Risolti Oggi** | Allarmi risolti nelle ultime 24 ore | Verde |
| **Totale** | Totale allarmi registrati nel sistema | Grigio |

### 7.2 Filtri

Usa il selettore in alto a destra per filtrare gli allarmi:
- **Tutti**: Mostra tutti gli allarmi (badge con totale)
- **Attivi**: Solo allarmi attivi + in attesa (badge rosso)
- **Risolti**: Solo allarmi risolti (badge verde)

### 7.3 Tabella Allarmi

La tabella mostra i dettagli di ogni allarme:

**Colonne:**
- **Severità**:
  - 🔴 **Critico**: Richiede intervento immediato
  - 🟡 **Attenzione**: Da monitorare
  - 🔵 **Info**: Solo informativo
- **Codice**: Codice allarme (es: W001, I001)
- **Messaggio**: Descrizione dell'allarme
- **Dispositivo**: Nome del dispositivo interessato
- **Stato**:
  - 🔴 **Attivo**: Non ancora preso in carico
  - 🟠 **Preso in carico**: In lavorazione
  - 🟢 **Risolto**: Completato
- **Data**: Quando è stato rilevato
- **Azioni**: Pulsanti per gestire l'allarme

### 7.4 Gestione Allarmi

Per ogni allarme puoi:

1. **Confermare** (se Attivo): Prende in carico l'allarme, cambia stato in "Preso in carico"
2. **Risolvi** (se Attivo o Preso in carico): Marca l'allarme come risolto

### 7.5 Alert Banner

Se ci sono allarmi critici attivi, vedrai un banner rosso in alto con:
- Numero di allarmi critici
- Messaggio: "Richiede attenzione immediata"

### 7.6 Tipi di Allarmi Comuni

| Codice | Severità | Descrizione | Azione Consigliata |
|--------|----------|-------------|-------------------|
| **W001** | Warning | Batteria sotto il 20% | Normale se di notte, verifica sistema |
| **I001** | Info | Produzione inferiore alla media | Controlla meteo, pulizia pannelli |
| **I002** | Info | Manutenzione programmata completata | Nessuna azione richiesta |
| **C001** | Critical | Perdita connessione inverter | Contattare assistenza |
| **C002** | Critical | Errore comunicazione batteria | Contattare assistenza |

### 7.7 Pulsanti Azione

- **🔄 Aggiorna**: Ricarica la lista allarmi
- **🕐 Storico**: Visualizza lo storico completo (funzionalità futura)

### 7.8 Notifiche Email

Le notifiche email vengono inviate automaticamente per:
- Allarmi critici (immediato)
- Allarmi di attenzione (raggruppati)
- Report giornaliero (se abilitato)
- Report settimanale (se abilitato)

**Configurazione Email:**
Vai su **Impostazioni → Notifiche** per configurare:
- Indirizzo email destinatario
- Tipi di allarmi da notificare
- Frequenza report

---

## 8. Impostazioni

La pagina **Impostazioni** permette di configurare il sistema e le preferenze utente.

### 8.1 Scheda Generale

**Nome Impianto**
- Personalizza il nome del tuo impianto (es: "Casa Tommasini")

**Lingua**
- Italiano (predefinito)
- English

**Fuso Orario**
- Europe/Rome (UTC+1) - predefinito
- Altro

**Valuta**
- Euro (€) - predefinito
- US Dollar ($)

**Tariffe Energia**
- **Prezzo Acquisto** (€/kWh): Costo dell'energia dalla rete (default: €0,25/kWh)
- **Prezzo Vendita** (€/kWh): Ricavo dalla vendita in rete (default: €0,10/kWh)

> Questi valori vengono usati per calcolare i risparmi economici nelle dashboard e analytics.

### 8.2 Scheda Notifiche

**Notifiche Email**
- Inserisci il tuo indirizzo email per ricevere le notifiche

**Interruttori On/Off:**
- ✅ **Allarmi Critici**: Notifica immediata per problemi gravi (consigliato: ON)
- ✅ **Avvisi**: Notifica per allarmi di attenzione (consigliato: ON)
- ⬜ **Report Giornaliero**: Riepilogo giornaliero produzione/consumo
- ✅ **Report Settimanale**: Riepilogo settimanale con analytics

**Soglie Allarme**
- **Batteria Bassa (%)**: Percentuale sotto la quale viene inviato un avviso (default: 20%)
- **Batteria Critica (%)**: Percentuale critica (default: 10%)

### 8.3 Scheda Edifici 🏢 NEW

**Lista Edifici**
Visualizza tutti gli edifici a cui hai accesso:
- Nome edificio
- Indirizzo
- Ruolo (Owner, Admin, Member, Viewer)
- Numero di dispositivi
- Temperatura attuale

**Azioni:**
- **Modifica**: Cambia nome o indirizzo dell'edificio
- **Membri**: Gestisci gli utenti con accesso all'edificio
- **Dispositivi**: Gestisci i dispositivi associati
- **Elimina**: Rimuovi l'edificio (solo Owner)

### 8.4 Scheda Dispositivi

**Dispositivi Configurati**
Mostra i dispositivi attualmente collegati:
- Thing Key (es: ZE1ES330J9E558)
- Tipo (es: Inverter Ibrido)
- Stato (🟢 Online / 🔴 Offline)
- Ultimo Aggiornamento

**Aggiungi Dispositivo**
- Funzionalità riservata all'amministratore
- Per aggiungere nuovi dispositivi, contattare il supporto

### 8.5 Scheda API

**Configurazione ZCS API**
Visualizza lo stato della connessione alle API ZCS Azzurro:
- **Endpoint**: URL delle API ZCS
- **Client Code**: Codice cliente (mascherato per sicurezza)
- **Stato Connessione**: 🟢 Connesso / 🔴 Disconnesso
- **Ultimo Sync**: Timestamp ultimo aggiornamento

**Intervalli di Aggiornamento**
- **Dati Real-time** (secondi): Frequenza aggiornamento dati istantanei (default: 60s)
- **Dati Storici** (minuti): Frequenza aggiornamento grafici (default: 15 min)

> **Nota**: Intervalli troppo brevi possono causare problemi di rate limiting con le API ZCS

### 8.6 Scheda Sistema

**Informazioni Sistema**
- **Versione**: v2.1.0
- **Build**: 2025-12-19
- **Backend**: FastAPI (Python)
- **Frontend**: React + Refine
- **Database**: PostgreSQL + InfluxDB
- **Cache**: Redis

**Manutenzione** (solo amministratori)
- 🔒 Backup Database
- 🔒 Verifica Integrità

### 8.7 Salvataggio Modifiche

Dopo aver modificato le impostazioni:
1. Clicca su **"Salva Modifiche"** in alto a destra
2. Vedrai una notifica di conferma: "Impostazioni salvate con successo!"
3. Le modifiche verranno applicate immediatamente

> **Nota**: Alcune modifiche (come gli intervalli di aggiornamento) potrebbero richiedere alcuni minuti per essere effettive.

---

## 9. Lettura Contatore Gas

> ⛽ **Coming Soon** - Funzionalità in sviluppo

### 9.1 Panoramica

SunPulse permette di registrare le letture del contatore gas per monitorare i consumi domestici. Le letture possono essere inserite in due modi:

| Modalità | Descrizione | Quando usarla |
|----------|-------------|---------------|
| **Manuale** | Inserisci il valore letto sul contatore | Sempre affidabile |
| **OCR da Foto** | Scatta una foto al contatore | Più veloce, evita errori di trascrizione |

### 9.2 Inserimento Manuale

1. Vai alla pagina **Contatori** dal menu laterale
2. Clicca su **Nuova Lettura**
3. Seleziona **Gas** come tipo contatore
4. Inserisci il valore letto (es. `12345.678`)
5. Seleziona la data della lettura
6. Aggiungi eventuali note
7. Clicca **Salva**

> ⚠️ **Nota**: Il sistema verifica che la nuova lettura sia maggiore della precedente

### 9.3 Lettura con OCR

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

### 9.4 Storico e Consumi

Nella sezione **Storico Letture** puoi:
- 📊 Vedere il grafico dei consumi nel tempo
- 📋 Consultare la tabella delle letture
- 📈 Calcolare il consumo tra due date
- 📥 Esportare i dati in CSV

### 9.5 Calcolo Consumo

Il consumo viene calcolato automaticamente:

```
Consumo = Lettura Attuale - Lettura Precedente
```

Esempio:
- Lettura 1 Dicembre: 12.345 m³
- Lettura 1 Gennaio: 12.489 m³
- **Consumo Dicembre**: 144 m³ (12.489 - 12.345)

---

## 10. Architettura Tecnica

### 10.1 Stack Tecnologico

**Frontend:**
- React 18.2
- Refine (framework admin dashboard)
- Ant Design (UI components)
- Auth0 (autenticazione)

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- Celery + Redis (task queue)
- PostgreSQL (database relazionale)
- InfluxDB (time series)

**Infrastruttura:**
- Docker & Docker Compose
- Traefik (reverse proxy + SSL)
- Nginx (static file serving)

### 10.2 Flusso Dati

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Pannelli    │──────▶│  Inverter    │──────▶│  ZCS Cloud   │
│  Solari      │       │  ZCS Azzurro │       │  API         │
└──────────────┘       └──────────────┘       └──────┬───────┘
                                                      │
                                                      ▼
                                              ┌──────────────┐
                                              │  SunPulse    │
                                              │  Backend     │
                                              └──────┬───────┘
                                                     │
                           ┌─────────────────────────┼─────────────────┐
                           ▼                         ▼                 ▼
                    ┌─────────────┐          ┌─────────────┐   ┌──────────┐
                    │ PostgreSQL  │          │   Redis     │   │ InfluxDB │
                    │ (metadata)  │          │   (cache)   │   │ (metrics)│
                    └─────────────┘          └─────────────┘   └──────────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │  Frontend    │
                                              │  (React)     │
                                              └──────────────┘
```

### 10.3 Aggiornamento Dati

**Task Automatici (Celery):**
- **collect_realtime_data**: ogni 2 minuti
- **collect_alarm_data**: ogni 30 secondi
- **health_check_task**: ogni 5 minuti

**Cache Strategy:**
- **L1 (Memory)**: 2 minuti per dati real-time
- **L2 (Redis)**: 15 minuti per dati storici recenti
- **L3 (PostgreSQL)**: Permanente per aggregati giornalieri

---

## 11. API ZCS Azzurro

### 11.1 Endpoint Base

```
POST https://third.zcsazzurroportal.com:19003/
Headers:
  - Authorization: Zcs <TOKEN>
  - client: <CLIENT_CODE>
  - Content-Type: application/json
```

### 11.2 Metodi Principali

#### realtimeData
Snapshot corrente di tutte le metriche

#### historicData
Serie temporali per grafici (max 24h per richiesta)

#### deviceAlarm
Stato allarmi attivi

#### deviceHistoricAlarm
Timeline storica allarmi (max 24h per richiesta)

> Per dettagli completi vedi `doc/Specifica API 1.8 del 10-03-2025 (IT)/input.md`

### 11.3 Limiti Rate Limiting

- **Massimo ~100 richieste/ora** (stima)
- **Finestra max 24 ore** per dati storici
- **Timeout connessione**: 30 secondi

---

## 12. Troubleshooting

### 12.1 Dashboard mostra dati a zero

**Sintomo**: Tutti i valori energetici mostrano 0 kWh

**Possibili Cause:**
1. È notte e non c'è produzione solare (normale)
2. Reset giornaliero a mezzanotte appena avvenuto
3. Cache non ancora aggiornata dopo il reset

**Soluzione:**
- Attendi 2-5 minuti per l'aggiornamento automatico
- Oppure clicca sul pulsante "Aggiorna" per forzare il refresh
- Verifica che l'inverter sia online (🟢)

### 12.2 Errore di connessione

**Sintomo**: "Impossibile caricare i dati" o spinner infinito

**Possibili Cause:**
1. Backend non raggiungibile
2. Problemi di rete
3. API ZCS temporaneamente non disponibile

**Soluzione:**
1. Verifica la connessione internet
2. Ricarica la pagina (F5 o Ctrl+R)
3. Controlla lo stato su **Impostazioni → API**
4. Se il problema persiste, contatta il supporto

### 12.3 Grafici non si caricano

**Sintomo**: Card dei grafici mostrano errore o sono vuote

**Possibili Cause:**
1. Dati storici non ancora disponibili
2. Dispositivo offline da più di 24 ore
3. Problema con database InfluxDB

**Soluzione:**
1. Attendi almeno 1 ora dopo la prima installazione
2. Verifica stato dispositivo nella pagina Dispositivi
3. Se persiste, contatta amministratore di sistema

### 12.4 Email notifiche non arrivano

**Sintomo**: Non ricevi email per allarmi o report

**Possibili Cause:**
1. Email non configurata correttamente
2. Email finisce in spam
3. Servizio Resend temporaneamente down

**Soluzione:**
1. Vai su **Impostazioni → Notifiche**
2. Verifica che l'email sia corretta
3. Controlla la cartella spam/posta indesiderata
4. Aggiungi `noreply@sunpulse.com` ai contatti attendibili
5. Clicca su "Invia Test" per verificare

### 12.5 Logout automatico

**Sintomo**: Vieni disconnesso frequentemente

**Possibili Cause:**
1. Token Auth0 scaduto (normale dopo 24h)
2. Browser cancella i cookie
3. Sessione scaduta per inattività

**Soluzione:**
- Comportamento normale, basta rifare login
- Se troppo frequente, verifica le impostazioni privacy del browser
- Assicurati che i cookie siano abilitati per il sito

### 12.6 Errori 500 (Internal Server Error)

**Sintomo**: Errore generico del server

**Possibili Cause:**
1. Bug nel backend
2. Database non risponde
3. API ZCS rate limiting

**Soluzione:**
1. Attendi qualche minuto e riprova
2. Segnala l'errore all'amministratore con:
   - Ora esatta dell'errore
   - Pagina dove è avvenuto
   - Azione che stavi compiendo

---

## 13. FAQ

### 13.1 Domande Generali

**Q: SunPulse funziona con altri inverter oltre a ZCS Azzurro?**
A: Attualmente SunPulse supporta solo inverter ZCS Azzurro con accesso alle API ZCS Portal. Il supporto per altri brand è in roadmap.

**Q: I miei dati sono al sicuro?**
A: Sì, SunPulse utilizza:
- Autenticazione sicura tramite Auth0
- Comunicazione HTTPS crittografata
- Database protetti con password
- Nessun dato condiviso con terze parti

**Q: Posso usare SunPulse da smartphone?**
A: Sì, l'interfaccia è completamente responsive e ottimizzata per mobile.

**Q: Quanto costa SunPulse?**
A: SunPulse è open source e gratuito. Devi solo sostenere i costi dell'hosting (server + database).

**Q: Posso gestire più edifici con lo stesso account?**
A: Sì, puoi creare e gestire più edifici. Ogni edificio ha i propri dispositivi, dati meteo e membri con accesso.

**Q: Come posso condividere l'accesso al mio impianto con altri familiari?**
A: Vai su Impostazioni → Edifici → [Edificio] → Gestisci Membri e invia un invito via email. Puoi scegliere il ruolo (Admin, Member, Viewer).

**Q: L'indirizzo dell'edificio è obbligatorio?**
A: Sì, l'indirizzo è necessario per determinare le coordinate GPS, che vengono usate per recuperare i dati meteo locali (temperatura, alba/tramonto, condizioni meteo).

### 13.2 Dati e Metriche

**Q: Perché l'energia giornaliera è diversa tra Dashboard e Analytics?**
A: La Dashboard mostra dati in tempo reale (aggiornati ogni 2 min), mentre Analytics usa dati aggregati salvati nel database a mezzanotte. Piccole differenze sono normali.

**Q: Come viene calcolato l'autoconsumo?**
A: Autoconsumo = Energia prodotta usata direttamente in casa (senza passare per rete o batteria). È calcolato automaticamente dall'inverter ZCS.

**Q: Cosa significa "Tasso di Autosufficienza"?**
A: È la percentuale del tuo consumo coperta da fonti proprie (solare + batteria). Più è alta, meno dipendi dalla rete elettrica.

**Q: Perché i totali storici non cambiano?**
A: I "Totali Storici" sono contatori cumulativi dall'installazione dell'impianto. Crescono sempre, non si resettano mai.

### 13.3 Batteria

**Q: Perché la batteria si scarica di notte?**
A: La batteria alimenta la casa quando i pannelli non producono (notte). È il comportamento corretto per massimizzare l'autoconsumo.

**Q: Cosa sono i "cicli batteria"?**
A: Un ciclo = carica completa (0→100%) + scarica completa (100→0%). Più cicli = batteria più "usata" (ma le batterie moderne durano migliaia di cicli).

**Q: Quando conviene caricare la batteria dalla rete?**
A: Dipende dalla tua tariffa elettrica. Se hai tariffe biorarie, conviene caricare di notte (F3) per usarla di giorno quando costa di più.

### 13.4 Allarmi

**Q: Ho ricevuto allarme "Batteria sotto 20%", devo preoccuparmi?**
A: No, è normale se hai consumato molto. La batteria si ricaricherà il giorno dopo con il sole. Preoccupati solo se persiste per più giorni.

**Q: Cosa significa "Produzione inferiore alla media"?**
A: L'impianto produce meno del solito. Possibili cause: giornata nuvolosa, pannelli sporchi, ombreggiamenti. Controlla e pulisci i pannelli se necessario.

**Q: Come disattivo le notifiche email?**
A: Vai su **Impostazioni → Notifiche** e disattiva gli interruttori delle notifiche che non vuoi ricevere.

### 13.5 Tecnico

**Q: Dove sono salvati i miei dati?**
A: I dati sono salvati su:
- **PostgreSQL**: metadata, configurazione, aggregati giornalieri
- **InfluxDB**: serie temporali per grafici
- **Redis**: cache temporanea (dati volatili)

**Q: Posso esportare i miei dati?**
A: Sì, puoi esportare i dati storici in CSV dalla pagina Analytics (funzionalità in roadmap).

**Q: Cosa succede se il server va offline?**
A: I dati in cache Redis vengono persi, ma quelli in PostgreSQL/InfluxDB sono al sicuro. Al riavvio il sistema riprende a raccogliere dati normalmente.

**Q: Posso personalizzare i grafici?**
A: Attualmente i grafici sono predefiniti. La personalizzazione avanzata è in roadmap per versioni future.

---

## 📞 Supporto

- **Repository**: https://github.com/giovannitommasini/sunpulse
- **Autore**: Giovanni Tommasini
- **Email**: tommasini.giovanni@gmail.com

---

*Made with ☀️ by Giovanni Tommasini - © 2025 SunPulse*

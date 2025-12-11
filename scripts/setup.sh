#!/bin/bash

# =============================================================================
# SunPulse - Script di Setup
# =============================================================================

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni di utilità
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica prerequisiti
check_prerequisites() {
    log_info "Verifica prerequisiti..."
    
    # Verifica Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker non è installato. Installalo da https://docker.com"
        exit 1
    fi
    
    # Verifica Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose non è installato."
        exit 1
    fi
    
    log_success "Tutti i prerequisiti sono soddisfatti"
}

# Crea file .env se non esiste
setup_environment() {
    log_info "Configurazione ambiente..."
    
    if [ ! -f .env ]; then
        log_info "Copia .env.example in .env..."
        cp .env.example .env
        log_warning "IMPORTANTE: Modifica il file .env con le tue configurazioni!"
        log_warning "Specialmente le password e le chiavi API ZCS/Auth0"
    else
        log_info "File .env già esistente"
    fi
}

# Crea cartelle necessarie
setup_directories() {
    log_info "Creazione cartelle necessarie..."
    
    # Cartelle con permessi specifici
    mkdir -p modules/postgres/data
    mkdir -p modules/influxdb/data
    mkdir -p modules/influxdb/config
    mkdir -p modules/mosquitto/data
    mkdir -p modules/n8n/data
    mkdir -p modules/n8n/workflows
    
    # Imposta permessi per servizi
    chmod 755 modules/postgres/data
    chmod 755 modules/influxdb/data
    chmod 755 modules/mosquitto/data
    chmod 755 modules/n8n/data
    
    log_success "Cartelle create con successo"
}

# Genera chiavi di sicurezza
generate_secrets() {
    log_info "Generazione chiavi di sicurezza..."
    
    # Genera SECRET_KEY se non presente nel .env
    if ! grep -q "SECRET_KEY=" .env || grep -q "your_super_secret" .env; then
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        log_success "SECRET_KEY generata"
    fi
    
    # Genera password Redis se non presente
    if ! grep -q "REDIS_PASSWORD=" .env || grep -q "secure_redis_password" .env; then
        REDIS_PASSWORD=$(openssl rand -base64 32)
        sed -i.bak "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
        log_success "Password Redis generata"
    fi
    
    # Genera password PostgreSQL se non presente
    if ! grep -q "POSTGRES_PASSWORD=" .env || grep -q "secure_postgres_password" .env; then
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
        log_success "Password PostgreSQL generata"
    fi
}

# Avvia servizi
start_services() {
    log_info "Avvio servizi Docker..."
    
    # Prima avvia solo i database per l'inizializzazione
    log_info "Avvio database..."
    docker-compose up -d postgres redis influxdb
    
    # Attendi che i database siano pronti
    log_info "Attesa inizializzazione database..."
    sleep 10
    
    # Verifica che PostgreSQL sia pronto
    while ! docker-compose exec -T postgres pg_isready -U postgres; do
        log_info "Attesa PostgreSQL..."
        sleep 2
    done
    
    # Avvia MQTT
    log_info "Avvio MQTT..."
    docker-compose up -d mosquitto
    
    # Avvia N8N
    log_info "Avvio N8N..."
    docker-compose up -d n8n
    
    # Avvia backend
    log_info "Avvio backend..."
    docker-compose up -d backend
    
    # Attendi che il backend sia pronto
    log_info "Attesa backend..."
    sleep 5
    
    # Verifica health del backend
    while ! curl -f http://localhost:8000/health &> /dev/null; do
        log_info "Attesa backend health check..."
        sleep 3
    done
    
    log_success "Tutti i servizi sono avviati!"
}

# Mostra informazioni di accesso
show_access_info() {
    log_success "=== SunPulse - Setup Completato ==="
    echo ""
    log_info "Servizi disponibili:"
    echo "  🌐 Backend API:      http://localhost:8000"
    echo "  📊 API Docs:         http://localhost:8000/docs"
    echo "  🔧 N8N:              http://localhost:5678"
    echo "  💾 InfluxDB:         http://localhost:8086"
    echo ""
    log_info "Credenziali predefinite:"
    echo "  N8N: admin / (vedi .env N8N_PASSWORD)"
    echo ""
    log_warning "NEXT STEPS:"
    echo "  1. Modifica il file .env con le tue configurazioni API ZCS e Auth0"
    echo "  2. Avvia il frontend quando pronto"
    echo "  3. Avvia nginx per il reverse proxy: docker-compose up -d nginx"
    echo ""
    log_info "Per vedere i logs: docker-compose logs -f [service]"
    log_info "Per fermare tutto: docker-compose down"
}

# Funzione principale
main() {
    echo "=============================================="
    echo "     SunPulse - Setup Script"
    echo "=============================================="
    echo ""
    
    check_prerequisites
    setup_environment
    setup_directories
    generate_secrets
    start_services
    show_access_info
}

# Esegui script principale
main "$@" 
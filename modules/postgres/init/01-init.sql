-- Script di inizializzazione database SunPulse
-- Eseguito automaticamente al primo avvio di PostgreSQL

-- Crea database per N8N se non esiste
CREATE DATABASE n8n;

-- Crea utente per l'applicazione con privilegi limitati
CREATE USER solar_app WITH ENCRYPTED PASSWORD 'solar_app_password';

-- Concedi privilegi al database principale
GRANT ALL PRIVILEGES ON DATABASE sunpulse TO solar_app;

-- Concedi privilegi al database N8N
GRANT ALL PRIVILEGES ON DATABASE n8n TO solar_app;

-- Schema iniziale per sunpulse
\c sunpulse;

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    picture TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Tabella permessi utente
CREATE TABLE IF NOT EXISTS user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER REFERENCES users(id),
    UNIQUE(user_id, permission, resource)
);

-- Tabella dispositivi
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    thing_key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    installation_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Configurazioni dispositivi
CREATE TABLE IF NOT EXISTS device_configurations (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    data_type VARCHAR(20) DEFAULT 'string',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, config_key)
);

-- Canali di notifica
CREATE TABLE IF NOT EXISTS notification_channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- email, telegram, ntfy, webhook
    config JSONB NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Regole di allarme
CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    condition_type VARCHAR(50) NOT NULL, -- threshold, change, offline
    condition_config JSONB NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Log notifiche
CREATE TABLE IF NOT EXISTS notifications_log (
    id SERIAL PRIMARY KEY,
    alert_rule_id INTEGER REFERENCES alert_rules(id) ON DELETE CASCADE,
    channel_id INTEGER REFERENCES notification_channels(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, retrying
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Log audit
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sessioni utente (opzionale, per tracking avanzato)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_devices_thing_key ON devices(thing_key);
CREATE INDEX IF NOT EXISTS idx_devices_active ON devices(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_log_status ON notifications_log(status);

-- Trigger per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Applica trigger alle tabelle necessarie
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_device_configurations_updated_at BEFORE UPDATE ON device_configurations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_channels_updated_at BEFORE UPDATE ON notification_channels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alert_rules_updated_at BEFORE UPDATE ON alert_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Dati di test iniziali (opzionale)
INSERT INTO users (auth0_id, email, name) VALUES
('auth0|test123', 'admin@sunpulse.local', 'Admin User')
ON CONFLICT (auth0_id) DO NOTHING;

INSERT INTO notification_channels (name, type, config) VALUES
('Email Default', 'email', '{"smtp_host": "localhost", "from": "noreply@sunpulse.local"}'),
('Telegram Admin', 'telegram', '{"bot_token": "", "chat_id": ""}')
ON CONFLICT DO NOTHING; 
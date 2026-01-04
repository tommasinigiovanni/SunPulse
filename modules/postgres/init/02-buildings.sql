-- ============================================================================
-- Migration: Buildings Architecture
-- SunPulse v2.2.0
-- Date: 2026-01-03
-- 
-- Introduces the Building entity as the central concept:
-- - Users -> Buildings (N:M relationship)
-- - Buildings -> Devices (1:N relationship)
-- - Buildings -> Weather (1:N time series)
-- ============================================================================

\c sunpulse;

-- ============================================================================
-- 1. Buildings Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    
    -- Address information (from Google Places)
    address VARCHAR(500) NOT NULL,
    address_components JSONB,
    place_id VARCHAR(100),
    
    -- GPS Coordinates
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Settings
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)  -- Auth0 user ID
);

-- Indexes for buildings
CREATE INDEX IF NOT EXISTS idx_buildings_created_by ON buildings(created_by);
CREATE INDEX IF NOT EXISTS idx_buildings_place_id ON buildings(place_id);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_buildings_updated_at ON buildings;
CREATE TRIGGER update_buildings_updated_at 
    BEFORE UPDATE ON buildings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE buildings IS 'Physical locations where PV devices are installed';
COMMENT ON COLUMN buildings.address_components IS 'Structured address from Google Places API';
COMMENT ON COLUMN buildings.place_id IS 'Google Place ID for address verification';

-- ============================================================================
-- 2. User Buildings Table (N:M relationship)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_buildings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,  -- Auth0 user ID
    building_id INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    
    -- Role: owner, admin, member, viewer
    role VARCHAR(50) DEFAULT 'member',
    
    -- Invitation info
    invited_by VARCHAR(255),
    invitation_email VARCHAR(255),
    invitation_token VARCHAR(255),
    invitation_accepted BOOLEAN DEFAULT true,
    
    -- Metadata
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT uq_user_building UNIQUE(user_id, building_id)
);

-- Indexes for user_buildings
CREATE INDEX IF NOT EXISTS idx_user_buildings_user_id ON user_buildings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_buildings_building_id ON user_buildings(building_id);
CREATE INDEX IF NOT EXISTS idx_user_buildings_role ON user_buildings(role);
CREATE INDEX IF NOT EXISTS idx_user_buildings_invitation_token ON user_buildings(invitation_token) WHERE invitation_token IS NOT NULL;

COMMENT ON TABLE user_buildings IS 'N:M relationship between users and buildings';
COMMENT ON COLUMN user_buildings.role IS 'User role: owner, admin, member, viewer';

-- ============================================================================
-- 3. Building Devices Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS building_devices (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    thing_key VARCHAR(100) NOT NULL,
    
    -- Device info
    name VARCHAR(255),
    device_type VARCHAR(50) DEFAULT 'inverter',  -- inverter, battery, meter
    
    -- Status
    status VARCHAR(20) DEFAULT 'unknown',  -- online, offline, warning, unknown
    last_seen TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT uq_building_device UNIQUE(building_id, thing_key)
);

-- Indexes for building_devices
CREATE INDEX IF NOT EXISTS idx_building_devices_building_id ON building_devices(building_id);
CREATE INDEX IF NOT EXISTS idx_building_devices_thing_key ON building_devices(thing_key);
CREATE INDEX IF NOT EXISTS idx_building_devices_status ON building_devices(status);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_building_devices_updated_at ON building_devices;
CREATE TRIGGER update_building_devices_updated_at 
    BEFORE UPDATE ON building_devices 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE building_devices IS 'ZCS devices associated with a building';
COMMENT ON COLUMN building_devices.thing_key IS 'ZCS device identifier';

-- ============================================================================
-- 4. Building Weather Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS building_weather (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    
    -- Temperature
    temperature DECIMAL(5, 2),  -- °C
    feels_like DECIMAL(5, 2),   -- °C
    temp_min DECIMAL(5, 2),     -- °C
    temp_max DECIMAL(5, 2),     -- °C
    
    -- Atmosphere
    humidity INTEGER,  -- %
    pressure INTEGER,  -- hPa
    
    -- Wind
    wind_speed DECIMAL(5, 2),  -- m/s
    wind_deg INTEGER,          -- degrees
    wind_gust DECIMAL(5, 2),   -- m/s
    
    -- Conditions
    weather_condition VARCHAR(50),    -- clear, clouds, rain, snow, etc.
    weather_description VARCHAR(100), -- Detailed description
    weather_icon VARCHAR(20),         -- Icon code from API
    
    -- Clouds and visibility
    clouds INTEGER,     -- % cloudiness
    visibility INTEGER, -- meters
    
    -- Sun times
    sunrise TIMESTAMP WITH TIME ZONE,
    sunset TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for building_weather
CREATE INDEX IF NOT EXISTS idx_building_weather_building_id ON building_weather(building_id);
CREATE INDEX IF NOT EXISTS idx_building_weather_fetched_at ON building_weather(fetched_at);
CREATE INDEX IF NOT EXISTS idx_building_weather_building_fetched ON building_weather(building_id, fetched_at DESC);

COMMENT ON TABLE building_weather IS 'Weather data for buildings (updated every 15 minutes)';
COMMENT ON COLUMN building_weather.weather_condition IS 'Main weather condition: clear, clouds, rain, snow, etc.';

-- ============================================================================
-- 5. User Onboarding Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_onboarding (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,  -- Auth0 user ID
    
    -- Wizard progress
    current_step INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'not_started',  -- not_started, in_progress, completed, skipped
    
    -- Reference to building created during wizard
    building_id INTEGER REFERENCES buildings(id) ON DELETE SET NULL,
    
    -- Step data (temporary storage during wizard)
    step_data JSONB DEFAULT '{}',
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for user_onboarding
CREATE INDEX IF NOT EXISTS idx_user_onboarding_user_id ON user_onboarding(user_id);
CREATE INDEX IF NOT EXISTS idx_user_onboarding_status ON user_onboarding(status);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_user_onboarding_updated_at ON user_onboarding;
CREATE TRIGGER update_user_onboarding_updated_at 
    BEFORE UPDATE ON user_onboarding 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_onboarding IS 'Tracks user onboarding wizard progress';
COMMENT ON COLUMN user_onboarding.step_data IS 'Temporary storage for form data during wizard';

-- ============================================================================
-- 6. User Settings - Add building reference (optional)
-- ============================================================================

-- Add default_building_id to user_settings if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_settings' AND column_name = 'default_building_id'
    ) THEN
        ALTER TABLE user_settings ADD COLUMN default_building_id INTEGER REFERENCES buildings(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- 7. Helper Functions
-- ============================================================================

-- Function to get user's buildings
CREATE OR REPLACE FUNCTION get_user_buildings(p_user_id VARCHAR)
RETURNS TABLE (
    building_id INTEGER,
    building_name VARCHAR,
    role VARCHAR,
    device_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.id,
        b.name,
        ub.role,
        COUNT(bd.id)
    FROM buildings b
    JOIN user_buildings ub ON b.id = ub.building_id
    LEFT JOIN building_devices bd ON b.id = bd.building_id
    WHERE ub.user_id = p_user_id
    GROUP BY b.id, b.name, ub.role
    ORDER BY ub.joined_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest weather for a building
CREATE OR REPLACE FUNCTION get_building_weather(p_building_id INTEGER)
RETURNS TABLE (
    temperature DECIMAL,
    feels_like DECIMAL,
    humidity INTEGER,
    weather_condition VARCHAR,
    weather_icon VARCHAR,
    fetched_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bw.temperature,
        bw.feels_like,
        bw.humidity,
        bw.weather_condition,
        bw.weather_icon,
        bw.fetched_at
    FROM building_weather bw
    WHERE bw.building_id = p_building_id
    ORDER BY bw.fetched_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to check user access to building
CREATE OR REPLACE FUNCTION check_building_access(p_user_id VARCHAR, p_building_id INTEGER, p_min_role VARCHAR DEFAULT 'viewer')
RETURNS BOOLEAN AS $$
DECLARE
    v_user_role VARCHAR;
    v_role_level INTEGER;
    v_min_role_level INTEGER;
BEGIN
    -- Get user's role for the building
    SELECT role INTO v_user_role
    FROM user_buildings
    WHERE user_id = p_user_id AND building_id = p_building_id;
    
    IF v_user_role IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Define role hierarchy: owner > admin > member > viewer
    v_role_level := CASE v_user_role
        WHEN 'owner' THEN 4
        WHEN 'admin' THEN 3
        WHEN 'member' THEN 2
        WHEN 'viewer' THEN 1
        ELSE 0
    END;
    
    v_min_role_level := CASE p_min_role
        WHEN 'owner' THEN 4
        WHEN 'admin' THEN 3
        WHEN 'member' THEN 2
        WHEN 'viewer' THEN 1
        ELSE 0
    END;
    
    RETURN v_role_level >= v_min_role_level;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. Clean up old weather data (retention policy: 30 days)
-- ============================================================================

-- Function to clean old weather data
CREATE OR REPLACE FUNCTION cleanup_old_weather_data(p_retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM building_weather
    WHERE fetched_at < CURRENT_TIMESTAMP - (p_retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Migration
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 02-buildings completed successfully at %', CURRENT_TIMESTAMP;
END $$;

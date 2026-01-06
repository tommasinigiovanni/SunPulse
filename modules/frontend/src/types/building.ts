/**
 * Building Types
 * Definisce i tipi per l'architettura Building-centric
 */

export interface Building {
  id: number;
  name: string;
  address: string;
  address_components?: AddressComponents;
  place_id?: string;
  latitude?: number;
  longitude?: number;
  timezone: string;
  created_at: string;
  updated_at?: string;
  created_by: number;
  current_weather?: BuildingWeather;
}

export interface AddressComponents {
  street_number?: string;
  route?: string;
  locality?: string;
  administrative_area_level_1?: string;
  administrative_area_level_2?: string;
  country?: string;
  postal_code?: string;
  formatted_address?: string;
}

export interface BuildingWeather {
  id: number;
  building_id: number;
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  weather_condition: string;
  weather_icon: string;
  sunrise?: string;
  sunset?: string;
  fetched_at: string;
}

export interface UserBuilding {
  id: number;
  user_id: number;
  building_id: number;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  invited_by?: number;
  joined_at: string;
  building?: Building;
}

export interface BuildingDevice {
  id: number;
  building_id: number;
  thing_key: string;
  name?: string;
  device_type?: string;
  status: 'online' | 'offline' | 'warning' | 'unknown';
  last_seen?: string;
}

export interface BuildingMember {
  id: number;
  user_id: number;
  user_email: string;
  user_name?: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  invited_by?: number;
  joined_at: string;
}

// Request Types
export interface CreateBuildingRequest {
  name: string;
  address: string;
  address_components?: AddressComponents;
  place_id?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}

export interface UpdateBuildingRequest {
  name?: string;
  address?: string;
  address_components?: AddressComponents;
  place_id?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}

export interface AddDeviceToBuildingRequest {
  thing_key: string;
  name?: string;
  device_type?: string;
}

export interface InviteMemberRequest {
  email: string;
  role: 'admin' | 'member' | 'viewer';
}

export interface UpdateMemberRoleRequest {
  role: 'admin' | 'member' | 'viewer';
}

// Google Places Types
export interface PlacePrediction {
  description: string;
  place_id: string;
  structured_formatting: {
    main_text: string;
    secondary_text: string;
  };
}

export interface PlaceDetails {
  place_id: string;
  formatted_address: string;
  address_components: AddressComponents;
  geometry: {
    location: {
      lat: number;
      lng: number;
    };
  };
  timezone?: string;
}

// API Response Types
export interface BuildingListResponse {
  buildings: Building[];
  total: number;
}

export interface BuildingDevicesResponse {
  devices: BuildingDevice[];
  total: number;
}

export interface BuildingMembersResponse {
  members: BuildingMember[];
  total: number;
}

export interface AddressAutocompleteResponse {
  predictions: PlacePrediction[];
}

export interface AddressDetailsResponse {
  place_id: string;
  formatted_address: string;
  address_components: AddressComponents;
  latitude: number;
  longitude: number;
  timezone: string;
}


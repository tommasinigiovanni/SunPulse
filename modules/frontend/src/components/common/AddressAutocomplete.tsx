/**
 * AddressAutocomplete Component
 * 
 * Componente per la ricerca di indirizzi con Google Places Autocomplete
 * Include preview mappa con marker della posizione selezionata
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Input, Card, List, Spin, Alert, Typography } from 'antd';
import { EnvironmentOutlined, LoadingOutlined } from '@ant-design/icons';
import type { PlacePrediction, AddressDetailsResponse } from '../../types/building';
import { axiosInstance } from '../../utils/api';
import { loadGoogleMapsAPI, isGoogleMapsLoaded } from '../../utils/googleMaps';

const { Text } = Typography;

interface AddressAutocompleteProps {
  value?: string;
  onChange?: (address: string, details: AddressDetailsResponse | null) => void;
  placeholder?: string;
  disabled?: boolean;
  showMap?: boolean;
  mapHeight?: number;
}

const AddressAutocomplete: React.FC<AddressAutocompleteProps> = ({
  value = '',
  onChange,
  placeholder = 'Cerca indirizzo...',
  disabled = false,
  showMap = true,
  mapHeight = 300,
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [predictions, setPredictions] = useState<PlacePrediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState<AddressDetailsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPredictions, setShowPredictions] = useState(false);
  const [googleMapsReady, setGoogleMapsReady] = useState(false);
  
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.Marker | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Carica Google Maps API
  useEffect(() => {
    const initGoogleMaps = async () => {
      try {
        if (!isGoogleMapsLoaded()) {
          await loadGoogleMapsAPI();
        }
        setGoogleMapsReady(true);
      } catch (error) {
        console.warn('Google Maps API non disponibile:', error);
        setError('Google Maps non disponibile. La ricerca indirizzo potrebbe non funzionare.');
      }
    };
    
    initGoogleMaps();
  }, []);

  // Inizializza la mappa
  useEffect(() => {
    if (!showMap || !mapRef.current || !googleMapsReady) return;

    // Verifica che Google Maps sia caricato
    if (typeof google === 'undefined' || !google.maps) {
      return;
    }

    // Crea mappa centrata sull'Italia
    const map = new google.maps.Map(mapRef.current, {
      center: { lat: 41.9028, lng: 12.4964 }, // Roma
      zoom: 6,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    mapInstanceRef.current = map;

    // Crea marker (inizialmente nascosto)
    const marker = new google.maps.Marker({
      map,
      visible: false,
    });

    markerRef.current = marker;

    return () => {
      marker.setMap(null);
    };
  }, [showMap, googleMapsReady]);

  // Aggiorna marker quando cambiano i dettagli
  useEffect(() => {
    if (!selectedDetails || !mapInstanceRef.current || !markerRef.current) return;

    const { latitude, longitude } = selectedDetails;
    const position = { lat: latitude, lng: longitude };

    // Aggiorna posizione marker
    markerRef.current.setPosition(position);
    markerRef.current.setVisible(true);

    // Centra mappa
    mapInstanceRef.current.setCenter(position);
    mapInstanceRef.current.setZoom(15);
  }, [selectedDetails]);

  // Fetch predictions da backend
  const fetchPredictions = useCallback(async (input: string) => {
    if (!input || input.length < 3) {
      setPredictions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axiosInstance.get<{ predictions: PlacePrediction[] }>(
        '/buildings/address/autocomplete',
        {
          params: { q: input },
        }
      );

      setPredictions(response.data.predictions || []);
      setShowPredictions(true);
    } catch (err: any) {
      console.error('Errore autocomplete:', err);
      setError(err.response?.data?.message || 'Errore durante la ricerca');
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch dettagli indirizzo da place_id
  const fetchPlaceDetails = useCallback(async (placeId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosInstance.get<AddressDetailsResponse>(
        `/buildings/address/details/${placeId}`
      );

      setSelectedDetails(response.data);
      
      // Notifica il parent component
      if (onChange) {
        onChange(response.data.formatted_address, response.data);
      }
    } catch (err: any) {
      console.error('Errore dettagli indirizzo:', err);
      setError(err.response?.data?.message || 'Errore durante il recupero dei dettagli');
    } finally {
      setLoading(false);
    }
  }, [onChange]);

  // Handler input change con debounce
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    // Clear previous timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer
    debounceTimerRef.current = setTimeout(() => {
      fetchPredictions(newValue);
    }, 300);
  };

  // Handler selezione prediction
  const handleSelectPrediction = (prediction: PlacePrediction) => {
    setInputValue(prediction.description);
    setShowPredictions(false);
    fetchPlaceDetails(prediction.place_id);
  };

  // Handler focus input
  const handleFocus = () => {
    if (predictions.length > 0) {
      setShowPredictions(true);
    }
  };

  // Handler blur input (con delay per permettere click su lista)
  const handleBlur = () => {
    setTimeout(() => {
      setShowPredictions(false);
    }, 200);
  };

  return (
    <div style={{ position: 'relative' }}>
      {/* Input con icona */}
      <Input
        value={inputValue}
        onChange={handleInputChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={disabled}
        prefix={<EnvironmentOutlined />}
        suffix={loading ? <LoadingOutlined spin /> : null}
        size="large"
      />

      {/* Lista predictions */}
      {showPredictions && predictions.length > 0 && (
        <Card
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            marginTop: 4,
            maxHeight: 300,
            overflow: 'auto',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          }}
          bodyStyle={{ padding: 0 }}
        >
          <List
            dataSource={predictions}
            renderItem={(prediction) => (
              <List.Item
                style={{
                  cursor: 'pointer',
                  padding: '12px 16px',
                }}
                onClick={() => handleSelectPrediction(prediction)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f5f5f5';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <List.Item.Meta
                  avatar={<EnvironmentOutlined style={{ fontSize: 18, color: '#1890ff' }} />}
                  title={prediction.structured_formatting.main_text}
                  description={
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {prediction.structured_formatting.secondary_text}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* Errore */}
      {error && (
        <Alert
          message={error}
          type="error"
          closable
          onClose={() => setError(null)}
          style={{ marginTop: 8 }}
        />
      )}

      {/* Mappa */}
      {showMap && (
        <div
          ref={mapRef}
          style={{
            width: '100%',
            height: mapHeight,
            marginTop: 16,
            borderRadius: 8,
            overflow: 'hidden',
            border: '1px solid #d9d9d9',
          }}
        />
      )}

      {/* Dettagli indirizzo selezionato */}
      {selectedDetails && (
        <Card size="small" style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <strong>Coordinate:</strong> {selectedDetails.latitude.toFixed(6)}, {selectedDetails.longitude.toFixed(6)}
            {selectedDetails.timezone && (
              <>
                {' | '}
                <strong>Timezone:</strong> {selectedDetails.timezone}
              </>
            )}
          </Text>
        </Card>
      )}
    </div>
  );
};

export default AddressAutocomplete;


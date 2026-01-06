/**
 * Google Maps API Loader
 * 
 * Carica dinamicamente l'API di Google Maps quando necessario
 */

let isLoading = false;
let isLoaded = false;
const callbacks: (() => void)[] = [];

/**
 * Carica l'API di Google Maps
 */
export const loadGoogleMapsAPI = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Già caricato
    if (isLoaded) {
      resolve();
      return;
    }

    // Già in caricamento - aggiungi callback
    if (isLoading) {
      callbacks.push(() => resolve());
      return;
    }

    // Controlla se la API key è configurata
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    if (!apiKey || apiKey === 'your-google-maps-api-key') {
      console.warn('Google Maps API key non configurata');
      reject(new Error('Google Maps API key non configurata'));
      return;
    }

    isLoading = true;

    // Crea script tag
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&language=it`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      isLoaded = true;
      isLoading = false;
      
      // Esegui tutti i callback in attesa
      callbacks.forEach(cb => cb());
      callbacks.length = 0;
      
      resolve();
    };

    script.onerror = () => {
      isLoading = false;
      const error = new Error('Errore nel caricamento di Google Maps API');
      reject(error);
    };

    document.head.appendChild(script);
  });
};

/**
 * Verifica se Google Maps è caricato
 */
export const isGoogleMapsLoaded = (): boolean => {
  return isLoaded && typeof window !== 'undefined' && typeof window.google !== 'undefined';
};

/**
 * Attende che Google Maps sia caricato
 */
export const waitForGoogleMaps = async (): Promise<void> => {
  if (isGoogleMapsLoaded()) {
    return;
  }
  return loadGoogleMapsAPI();
};


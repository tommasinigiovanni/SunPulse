"""
Google Places Service for SunPulse

Provides address autocomplete and geocoding using Google Places API.
"""
import httpx
import structlog
from typing import Optional, List, Dict, Any

from app.config.settings import get_settings
from app.models.building import (
    AddressAutocompleteResult,
    AddressAutocompleteResponse,
    AddressDetailsResponse
)

logger = structlog.get_logger()


class GooglePlacesService:
    """Service for Google Places API interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_MAPS_API_KEY
        
        # API endpoints
        self.autocomplete_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.timezone_url = "https://maps.googleapis.com/maps/api/timezone/json"
    
    @property
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    async def autocomplete(
        self, 
        query: str,
        language: str = "it",
        types: str = "address",
        components: str = "country:it"
    ) -> AddressAutocompleteResponse:
        """
        Search for addresses using Google Places Autocomplete
        
        Args:
            query: Search query string
            language: Language for results
            types: Types of places to return (address, geocode, establishment)
            components: Restrict to country (e.g., country:it)
            
        Returns:
            List of autocomplete suggestions
        """
        if not self.is_configured:
            logger.warning("Google Places API key not configured")
            return AddressAutocompleteResponse(results=[])
        
        if not query or len(query) < 3:
            return AddressAutocompleteResponse(results=[])
        
        try:
            params = {
                "input": query,
                "key": self.api_key,
                "language": language,
                "types": types,
            }
            
            if components:
                params["components"] = components
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.autocomplete_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                if data.get("status") == "ZERO_RESULTS":
                    return AddressAutocompleteResponse(results=[])
                logger.error(f"Google Places API error: {data.get('status')}")
                return AddressAutocompleteResponse(results=[])
            
            results = []
            for prediction in data.get("predictions", []):
                structured = prediction.get("structured_formatting", {})
                results.append(AddressAutocompleteResult(
                    place_id=prediction.get("place_id", ""),
                    description=prediction.get("description", ""),
                    main_text=structured.get("main_text", ""),
                    secondary_text=structured.get("secondary_text")
                ))
            
            return AddressAutocompleteResponse(results=results)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in Google Places autocomplete: {e}")
            return AddressAutocompleteResponse(results=[])
        except Exception as e:
            logger.error(f"Error in Google Places autocomplete: {e}", exc_info=True)
            return AddressAutocompleteResponse(results=[])
    
    async def get_place_details(
        self, 
        place_id: str,
        language: str = "it"
    ) -> Optional[AddressDetailsResponse]:
        """
        Get details for a place including coordinates
        
        Args:
            place_id: Google Place ID
            language: Language for results
            
        Returns:
            Address details with coordinates
        """
        if not self.is_configured:
            logger.warning("Google Places API key not configured")
            return None
        
        try:
            params = {
                "place_id": place_id,
                "key": self.api_key,
                "language": language,
                "fields": "formatted_address,geometry,address_components"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.details_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"Google Places Details API error: {data.get('status')}")
                return None
            
            result = data.get("result", {})
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            # Parse address components
            address_components = self._parse_address_components(
                result.get("address_components", [])
            )
            
            lat = location.get("lat")
            lng = location.get("lng")
            
            # Get timezone for coordinates
            timezone = await self._get_timezone(lat, lng) if lat and lng else None
            
            return AddressDetailsResponse(
                place_id=place_id,
                formatted_address=result.get("formatted_address", ""),
                address_components=address_components,
                latitude=lat,
                longitude=lng,
                timezone=timezone
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in Google Places details: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in Google Places details: {e}", exc_info=True)
            return None
    
    async def geocode(
        self, 
        address: str,
        language: str = "it"
    ) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to get coordinates
        
        Args:
            address: Full address string
            language: Language for results
            
        Returns:
            Dict with lat, lng and address components
        """
        if not self.is_configured:
            logger.warning("Google Maps API key not configured")
            return None
        
        try:
            params = {
                "address": address,
                "key": self.api_key,
                "language": language
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.geocode_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                logger.warning(f"Geocoding failed for: {address}")
                return None
            
            result = data["results"][0]
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            return {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
                "formatted_address": result.get("formatted_address"),
                "place_id": result.get("place_id"),
                "address_components": self._parse_address_components(
                    result.get("address_components", [])
                )
            }
            
        except Exception as e:
            logger.error(f"Error in geocoding: {e}", exc_info=True)
            return None
    
    async def _get_timezone(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[str]:
        """Get timezone for coordinates"""
        if not self.is_configured:
            return None
        
        try:
            import time
            
            params = {
                "location": f"{latitude},{longitude}",
                "timestamp": int(time.time()),
                "key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.timezone_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                return None
            
            return data.get("timeZoneId")
            
        except Exception as e:
            logger.error(f"Error getting timezone: {e}")
            return None
    
    def _parse_address_components(
        self, 
        components: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Parse Google address components into a flat dict"""
        result = {}
        
        type_mapping = {
            "street_number": "street_number",
            "route": "street",
            "locality": "city",
            "administrative_area_level_2": "province",
            "administrative_area_level_1": "region",
            "country": "country",
            "postal_code": "postal_code"
        }
        
        for component in components:
            types = component.get("types", [])
            for addr_type in types:
                if addr_type in type_mapping:
                    result[type_mapping[addr_type]] = component.get("long_name", "")
                    # Also store short_name for country
                    if addr_type == "country":
                        result["country_code"] = component.get("short_name", "")
                    break
        
        return result


# Singleton instance
_google_places_service: Optional[GooglePlacesService] = None


def get_google_places_service() -> GooglePlacesService:
    """Get or create the Google Places service singleton"""
    global _google_places_service
    if _google_places_service is None:
        _google_places_service = GooglePlacesService()
    return _google_places_service

"""
Weather Service for SunPulse

Fetches weather data from external APIs (OpenWeatherMap or WeatherAPI)
and stores it for each building.
"""
import httpx
import structlog
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.building import Building, BuildingWeather, BuildingWeatherResponse

logger = structlog.get_logger()


class WeatherService:
    """Service for fetching and storing weather data for buildings"""
    
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.WEATHER_API_PROVIDER
        self.api_key = self.settings.weather_api_key
        
        # API endpoints
        self.openweathermap_url = "https://api.openweathermap.org/data/2.5/weather"
        self.weatherapi_url = "https://api.weatherapi.com/v1/current.json"
    
    async def fetch_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather from external API
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            
        Returns:
            Weather data dict or None if failed
        """
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return None
        
        try:
            if self.provider == "openweathermap":
                return await self._fetch_openweathermap(latitude, longitude)
            elif self.provider == "weatherapi":
                return await self._fetch_weatherapi(latitude, longitude)
            else:
                logger.error(f"Unknown weather provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Error fetching weather: {e}", exc_info=True)
            return None
    
    async def _fetch_openweathermap(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Fetch from OpenWeatherMap API"""
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric",  # Celsius
            "lang": "it"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.openweathermap_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Parse OpenWeatherMap response
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        sys = data.get("sys", {})
        
        return {
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "wind_deg": wind.get("deg"),
            "wind_gust": wind.get("gust"),
            "weather_condition": weather.get("main", "").lower(),
            "weather_description": weather.get("description"),
            "weather_icon": weather.get("icon"),
            "clouds": clouds.get("all"),
            "visibility": data.get("visibility"),
            "sunrise": datetime.fromtimestamp(sys.get("sunrise", 0), tz=timezone.utc) if sys.get("sunrise") else None,
            "sunset": datetime.fromtimestamp(sys.get("sunset", 0), tz=timezone.utc) if sys.get("sunset") else None,
        }
    
    async def _fetch_weatherapi(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Fetch from WeatherAPI.com"""
        params = {
            "key": self.api_key,
            "q": f"{latitude},{longitude}",
            "lang": "it"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.weatherapi_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Parse WeatherAPI response
        current = data.get("current", {})
        condition = current.get("condition", {})
        
        return {
            "temperature": current.get("temp_c"),
            "feels_like": current.get("feelslike_c"),
            "temp_min": None,  # Not provided by WeatherAPI in current endpoint
            "temp_max": None,
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure_mb"),
            "wind_speed": current.get("wind_kph", 0) / 3.6 if current.get("wind_kph") else None,  # Convert to m/s
            "wind_deg": current.get("wind_degree"),
            "wind_gust": current.get("gust_kph", 0) / 3.6 if current.get("gust_kph") else None,
            "weather_condition": self._map_weatherapi_condition(condition.get("code")),
            "weather_description": condition.get("text"),
            "weather_icon": condition.get("icon"),
            "clouds": current.get("cloud"),
            "visibility": int(current.get("vis_km", 0) * 1000) if current.get("vis_km") else None,
            "sunrise": None,  # Requires astronomy endpoint
            "sunset": None,
        }
    
    def _map_weatherapi_condition(self, code: Optional[int]) -> str:
        """Map WeatherAPI condition codes to simple conditions"""
        if code is None:
            return "unknown"
        
        # Simplified mapping
        if code == 1000:
            return "clear"
        elif code in [1003, 1006, 1009]:
            return "clouds"
        elif code in [1030, 1135, 1147]:
            return "mist"
        elif code in [1063, 1150, 1153, 1180, 1183, 1186, 1189, 1192, 1195, 1240, 1243, 1246]:
            return "rain"
        elif code in [1066, 1114, 1117, 1210, 1213, 1216, 1219, 1222, 1225, 1255, 1258]:
            return "snow"
        elif code in [1087, 1273, 1276, 1279, 1282]:
            return "thunderstorm"
        else:
            return "clouds"
    
    async def update_building_weather(
        self, 
        db: Session, 
        building: Building
    ) -> Optional[BuildingWeather]:
        """
        Fetch and store weather for a building
        
        Args:
            db: Database session
            building: Building to update weather for
            
        Returns:
            Created BuildingWeather or None if failed
        """
        if not building.latitude or not building.longitude:
            logger.warning(f"Building {building.id} has no coordinates")
            return None
        
        # Fetch weather data
        weather_data = await self.fetch_weather(building.latitude, building.longitude)
        
        if not weather_data:
            logger.error(f"Failed to fetch weather for building {building.id}")
            return None
        
        # Create weather record
        weather = BuildingWeather(
            building_id=building.id,
            temperature=weather_data.get("temperature"),
            feels_like=weather_data.get("feels_like"),
            temp_min=weather_data.get("temp_min"),
            temp_max=weather_data.get("temp_max"),
            humidity=weather_data.get("humidity"),
            pressure=weather_data.get("pressure"),
            wind_speed=weather_data.get("wind_speed"),
            wind_deg=weather_data.get("wind_deg"),
            wind_gust=weather_data.get("wind_gust"),
            weather_condition=weather_data.get("weather_condition"),
            weather_description=weather_data.get("weather_description"),
            weather_icon=weather_data.get("weather_icon"),
            clouds=weather_data.get("clouds"),
            visibility=weather_data.get("visibility"),
            sunrise=weather_data.get("sunrise"),
            sunset=weather_data.get("sunset"),
            fetched_at=datetime.now(timezone.utc)
        )
        
        db.add(weather)
        db.commit()
        db.refresh(weather)
        
        logger.info(
            f"Updated weather for building {building.id}: "
            f"{weather.temperature}°C, {weather.weather_condition}"
        )
        
        return weather
    
    async def update_all_buildings_weather(self, db: Session) -> Dict[str, Any]:
        """
        Update weather for all buildings
        
        Args:
            db: Database session
            
        Returns:
            Summary of updates
        """
        buildings = db.query(Building).filter(
            Building.latitude.isnot(None),
            Building.longitude.isnot(None)
        ).all()
        
        success_count = 0
        error_count = 0
        
        for building in buildings:
            try:
                result = await self.update_building_weather(db, building)
                if result:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Error updating weather for building {building.id}: {e}")
                error_count += 1
        
        return {
            "total_buildings": len(buildings),
            "success": success_count,
            "errors": error_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_latest_weather(
        self, 
        db: Session, 
        building_id: int
    ) -> Optional[BuildingWeatherResponse]:
        """
        Get the latest weather for a building
        
        Args:
            db: Database session
            building_id: Building ID
            
        Returns:
            Latest weather data or None
        """
        weather = db.query(BuildingWeather).filter(
            BuildingWeather.building_id == building_id
        ).order_by(
            BuildingWeather.fetched_at.desc()
        ).first()
        
        if not weather:
            return None
        
        return BuildingWeatherResponse(
            temperature=weather.temperature,
            feels_like=weather.feels_like,
            humidity=weather.humidity,
            pressure=weather.pressure,
            wind_speed=weather.wind_speed,
            weather_condition=weather.weather_condition,
            weather_description=weather.weather_description,
            weather_icon=weather.weather_icon,
            clouds=weather.clouds,
            sunrise=weather.sunrise,
            sunset=weather.sunset,
            fetched_at=weather.fetched_at
        )
    
    def get_weather_history(
        self, 
        db: Session, 
        building_id: int,
        hours: int = 24
    ) -> List[BuildingWeatherResponse]:
        """
        Get weather history for a building
        
        Args:
            db: Database session
            building_id: Building ID
            hours: Hours of history to fetch
            
        Returns:
            List of weather data
        """
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        weather_list = db.query(BuildingWeather).filter(
            BuildingWeather.building_id == building_id,
            BuildingWeather.fetched_at >= cutoff
        ).order_by(
            BuildingWeather.fetched_at.desc()
        ).all()
        
        return [
            BuildingWeatherResponse(
                temperature=w.temperature,
                feels_like=w.feels_like,
                humidity=w.humidity,
                pressure=w.pressure,
                wind_speed=w.wind_speed,
                weather_condition=w.weather_condition,
                weather_description=w.weather_description,
                weather_icon=w.weather_icon,
                clouds=w.clouds,
                sunrise=w.sunrise,
                sunset=w.sunset,
                fetched_at=w.fetched_at
            )
            for w in weather_list
        ]


# Singleton instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the weather service singleton"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

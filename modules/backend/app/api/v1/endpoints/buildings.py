"""
Buildings Endpoints - Gestione edifici

Endpoints per la gestione degli edifici, dispositivi associati,
membri e dati meteo.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timezone
import structlog

from sqlalchemy.orm import Session

from ....auth import get_current_user, User
from ....database import get_db
from ....services.building_service import get_building_service
from ....services.weather_service import get_weather_service
from ....services.google_places_service import get_google_places_service
from ....models.building import (
    BuildingCreate,
    BuildingUpdate,
    BuildingResponse,
    BuildingListResponse,
    BuildingDeviceCreate,
    BuildingDeviceResponse,
    BuildingMemberResponse,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
    BuildingWeatherResponse,
    BuildingWeatherHistoryResponse,
    AddressAutocompleteResponse,
    AddressDetailsResponse,
)

logger = structlog.get_logger()

router = APIRouter()


# ==============================================================================
# Buildings CRUD
# ==============================================================================

@router.get("/", response_model=BuildingListResponse)
async def list_buildings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista tutti gli edifici accessibili dall'utente
    
    Returns:
        Lista di edifici con conteggio dispositivi e temperatura attuale
    """
    service = get_building_service()
    buildings = service.get_user_buildings(db, current_user.id)
    
    return BuildingListResponse(
        buildings=buildings,
        total=len(buildings)
    )


@router.post("/", response_model=BuildingResponse, status_code=201)
async def create_building(
    building_data: BuildingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo edificio
    
    L'utente che crea l'edificio diventa automaticamente il proprietario (owner).
    
    Args:
        building_data: Dati dell'edificio (nome, indirizzo, coordinate)
        
    Returns:
        Edificio creato
    """
    service = get_building_service()
    
    try:
        building = service.create_building(db, current_user.id, building_data)
        
        # Trigger initial weather fetch if coordinates available
        if building.latitude and building.longitude:
            weather_service = get_weather_service()
            try:
                await weather_service.update_building_weather(db, building)
            except Exception as e:
                logger.warning(f"Failed to fetch initial weather: {e}")
        
        # Get response with device count
        buildings = service.get_user_buildings(db, current_user.id)
        for b in buildings:
            if b.id == building.id:
                return b
        
        # Fallback
        return BuildingResponse(
            id=building.id,
            name=building.name,
            address=building.address,
            place_id=building.place_id,
            latitude=building.latitude,
            longitude=building.longitude,
            timezone=building.timezone,
            created_at=building.created_at,
            updated_at=building.updated_at,
            device_count=0
        )
        
    except Exception as e:
        logger.error(f"Error creating building: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Errore nella creazione dell'edificio")


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene i dettagli di un edificio
    
    Args:
        building_id: ID dell'edificio
        
    Returns:
        Dettagli edificio
    """
    service = get_building_service()
    
    # Check access
    if not service.check_access(db, current_user.id, building_id):
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    building = service.get_building(db, building_id, current_user.id)
    if not building:
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    # Get device count
    devices = service.get_devices(db, building_id)
    
    # Get weather
    weather_service = get_weather_service()
    weather = weather_service.get_latest_weather(db, building_id)
    
    return BuildingResponse(
        id=building.id,
        name=building.name,
        address=building.address,
        place_id=building.place_id,
        latitude=building.latitude,
        longitude=building.longitude,
        timezone=building.timezone,
        created_at=building.created_at,
        updated_at=building.updated_at,
        device_count=len(devices),
        current_temperature=weather.temperature if weather else None,
        weather_condition=weather.weather_condition if weather else None
    )


@router.put("/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: int,
    update_data: BuildingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un edificio (solo admin/owner)
    
    Args:
        building_id: ID dell'edificio
        update_data: Dati da aggiornare
        
    Returns:
        Edificio aggiornato
    """
    service = get_building_service()
    
    building = service.update_building(db, building_id, current_user.id, update_data)
    if not building:
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a modificare questo edificio"
        )
    
    # Get updated response
    devices = service.get_devices(db, building_id)
    weather_service = get_weather_service()
    weather = weather_service.get_latest_weather(db, building_id)
    
    return BuildingResponse(
        id=building.id,
        name=building.name,
        address=building.address,
        place_id=building.place_id,
        latitude=building.latitude,
        longitude=building.longitude,
        timezone=building.timezone,
        created_at=building.created_at,
        updated_at=building.updated_at,
        device_count=len(devices),
        current_temperature=weather.temperature if weather else None,
        weather_condition=weather.weather_condition if weather else None
    )


@router.delete("/{building_id}", status_code=204)
async def delete_building(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un edificio (solo owner)
    
    ATTENZIONE: Questa azione elimina anche tutti i dispositivi 
    e dati storici associati.
    
    Args:
        building_id: ID dell'edificio
    """
    service = get_building_service()
    
    if not service.delete_building(db, building_id, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a eliminare questo edificio"
        )


# ==============================================================================
# Devices Management
# ==============================================================================

@router.get("/{building_id}/devices", response_model=List[BuildingDeviceResponse])
async def list_building_devices(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista i dispositivi di un edificio
    
    Args:
        building_id: ID dell'edificio
        
    Returns:
        Lista dispositivi
    """
    service = get_building_service()
    
    if not service.check_access(db, current_user.id, building_id):
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    return service.get_devices(db, building_id)


@router.post("/{building_id}/devices", response_model=BuildingDeviceResponse, status_code=201)
async def add_device_to_building(
    building_id: int,
    device_data: BuildingDeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiunge un dispositivo all'edificio
    
    Args:
        building_id: ID dell'edificio
        device_data: Dati dispositivo (thing_key, nome)
        
    Returns:
        Dispositivo creato
    """
    service = get_building_service()
    
    device = service.add_device(db, building_id, current_user.id, device_data)
    if not device:
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato ad aggiungere dispositivi"
        )
    
    return BuildingDeviceResponse(
        id=device.id,
        building_id=device.building_id,
        thing_key=device.thing_key,
        name=device.name,
        device_type=device.device_type,
        status=device.status,
        last_seen=device.last_seen,
        created_at=device.created_at
    )


@router.delete("/{building_id}/devices/{device_id}", status_code=204)
async def remove_device_from_building(
    building_id: int,
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rimuove un dispositivo dall'edificio (solo admin/owner)
    
    Args:
        building_id: ID dell'edificio
        device_id: ID del dispositivo
    """
    service = get_building_service()
    
    if not service.remove_device(db, building_id, device_id, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a rimuovere dispositivi"
        )


# ==============================================================================
# Members Management
# ==============================================================================

@router.get("/{building_id}/members", response_model=List[BuildingMemberResponse])
async def list_building_members(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista i membri di un edificio
    
    Args:
        building_id: ID dell'edificio
        
    Returns:
        Lista membri con ruoli
    """
    service = get_building_service()
    
    if not service.check_access(db, current_user.id, building_id):
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    return service.get_members(db, building_id)


@router.post("/{building_id}/members", response_model=BuildingMemberResponse, status_code=201)
async def invite_member(
    building_id: int,
    invite_data: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invita un utente all'edificio (solo admin/owner)
    
    Args:
        building_id: ID dell'edificio
        invite_data: Email e ruolo dell'invitato
        
    Returns:
        Membro creato
    """
    service = get_building_service()
    
    member = service.add_member(
        db, 
        building_id, 
        current_user.id,
        invite_data.email,
        invite_data.role
    )
    
    if not member:
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a invitare membri"
        )
    
    # TODO: Send invitation email
    
    return BuildingMemberResponse(
        user_id=member.user_id,
        email=member.invitation_email,
        name=None,
        role=member.role,
        joined_at=member.joined_at,
        invitation_accepted=member.invitation_accepted
    )


@router.put("/{building_id}/members/{user_id}", status_code=200)
async def update_member_role(
    building_id: int,
    user_id: str,
    role_data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna il ruolo di un membro (solo admin/owner)
    
    Args:
        building_id: ID dell'edificio
        user_id: ID dell'utente da modificare
        role_data: Nuovo ruolo
    """
    service = get_building_service()
    
    if not service.update_member_role(db, building_id, current_user.id, user_id, role_data.role):
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a modificare ruoli"
        )
    
    return {"message": "Ruolo aggiornato con successo"}


@router.delete("/{building_id}/members/{user_id}", status_code=204)
async def remove_member(
    building_id: int,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rimuove un membro dall'edificio (solo admin/owner)
    
    Non è possibile rimuovere il proprietario.
    
    Args:
        building_id: ID dell'edificio
        user_id: ID dell'utente da rimuovere
    """
    service = get_building_service()
    
    if not service.remove_member(db, building_id, current_user.id, user_id):
        raise HTTPException(
            status_code=403, 
            detail="Non autorizzato a rimuovere membri"
        )


# ==============================================================================
# Weather
# ==============================================================================

@router.get("/{building_id}/weather", response_model=BuildingWeatherResponse)
async def get_building_weather(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene i dati meteo attuali dell'edificio
    
    Args:
        building_id: ID dell'edificio
        
    Returns:
        Dati meteo
    """
    building_service = get_building_service()
    
    if not building_service.check_access(db, current_user.id, building_id):
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    weather_service = get_weather_service()
    weather = weather_service.get_latest_weather(db, building_id)
    
    if not weather:
        raise HTTPException(status_code=404, detail="Dati meteo non disponibili")
    
    return weather


@router.get("/{building_id}/weather/history", response_model=BuildingWeatherHistoryResponse)
async def get_building_weather_history(
    building_id: int,
    hours: int = Query(24, ge=1, le=168, description="Ore di storico (max 168 = 7 giorni)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene lo storico meteo dell'edificio
    
    Args:
        building_id: ID dell'edificio
        hours: Numero di ore di storico (default 24, max 168)
        
    Returns:
        Lista dati meteo
    """
    building_service = get_building_service()
    
    if not building_service.check_access(db, current_user.id, building_id):
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    weather_service = get_weather_service()
    history = weather_service.get_weather_history(db, building_id, hours)
    
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    
    return BuildingWeatherHistoryResponse(
        building_id=building_id,
        history=history,
        period_start=now - timedelta(hours=hours),
        period_end=now
    )


@router.post("/{building_id}/weather/refresh", response_model=BuildingWeatherResponse)
async def refresh_building_weather(
    building_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Forza l'aggiornamento dei dati meteo
    
    Args:
        building_id: ID dell'edificio
        
    Returns:
        Nuovi dati meteo
    """
    building_service = get_building_service()
    
    if not building_service.check_access(db, current_user.id, building_id, min_role="member"):
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    building = building_service.get_building(db, building_id, current_user.id)
    if not building:
        raise HTTPException(status_code=404, detail="Edificio non trovato")
    
    weather_service = get_weather_service()
    weather = await weather_service.update_building_weather(db, building)
    
    if not weather:
        raise HTTPException(status_code=500, detail="Impossibile aggiornare i dati meteo")
    
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


# ==============================================================================
# Address Autocomplete
# ==============================================================================

@router.get("/address/autocomplete", response_model=AddressAutocompleteResponse)
async def address_autocomplete(
    q: str = Query(..., min_length=3, description="Query di ricerca"),
    current_user: User = Depends(get_current_user)
):
    """
    Ricerca indirizzi con autocompletamento (Google Places)
    
    Args:
        q: Stringa di ricerca (minimo 3 caratteri)
        
    Returns:
        Lista suggerimenti indirizzi
    """
    places_service = get_google_places_service()
    
    if not places_service.is_configured:
        raise HTTPException(
            status_code=503, 
            detail="Servizio indirizzi non configurato"
        )
    
    return await places_service.autocomplete(q)


@router.get("/address/details/{place_id}", response_model=AddressDetailsResponse)
async def get_address_details(
    place_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Ottiene i dettagli di un indirizzo (coordinate, componenti)
    
    Args:
        place_id: Google Place ID
        
    Returns:
        Dettagli indirizzo con coordinate GPS
    """
    places_service = get_google_places_service()
    
    if not places_service.is_configured:
        raise HTTPException(
            status_code=503, 
            detail="Servizio indirizzi non configurato"
        )
    
    details = await places_service.get_place_details(place_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Indirizzo non trovato")
    
    return details

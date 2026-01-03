"""
Onboarding Endpoints - Wizard di configurazione iniziale

Endpoints per gestire il flusso di onboarding degli utenti.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import structlog

from sqlalchemy.orm import Session

from ....auth import get_current_user, User
from ....database import get_db
from ....services.onboarding_service import get_onboarding_service
from ....models.building import (
    OnboardingStatusResponse,
    OnboardingStepUpdate,
    OnboardingDeviceValidation,
    OnboardingDeviceValidationResponse,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene lo stato del wizard di onboarding
    
    Returns:
        Status corrente del wizard (step, status, dati salvati)
    """
    service = get_onboarding_service()
    return service.get_status(db, current_user.id)


@router.get("/should-show", response_model=bool)
async def should_show_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica se mostrare il wizard di onboarding
    
    Il wizard viene mostrato se:
    - L'utente non ha mai completato/saltato il wizard
    - L'utente non ha edifici associati
    
    Returns:
        True se il wizard deve essere mostrato
    """
    service = get_onboarding_service()
    return not service.is_completed(db, current_user.id)


@router.post("/start", response_model=OnboardingStatusResponse)
async def start_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Avvia il wizard di onboarding
    
    Returns:
        Status del wizard aggiornato
    """
    service = get_onboarding_service()
    return service.start_wizard(db, current_user.id)


@router.put("/step/{step}", response_model=OnboardingStatusResponse)
async def save_onboarding_step(
    step: int,
    step_data: OnboardingStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Salva i dati di uno step e avanza al successivo
    
    Step disponibili:
    1. Welcome - Benvenuto (nessun dato richiesto)
    2. Building - Creazione edificio (name, address, place_id, coordinates)
    3. Devices - Aggiunta dispositivi (lista di thing_key)
    4. Notifications - Preferenze notifiche (email, flags)
    5. Summary - Riepilogo (nessun dato richiesto)
    
    Args:
        step: Numero dello step (1-5)
        step_data: Dati del form dello step
        
    Returns:
        Status del wizard aggiornato
    """
    if step < 1 or step > 5:
        raise HTTPException(status_code=400, detail="Step non valido (1-5)")
    
    service = get_onboarding_service()
    
    try:
        return service.save_step(db, current_user.id, step, step_data.step_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving onboarding step {step}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Errore nel salvataggio dello step")


@router.post("/complete", response_model=OnboardingStatusResponse)
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Completa il wizard di onboarding
    
    Marca il wizard come completato e redirige l'utente alla dashboard.
    
    Returns:
        Status del wizard aggiornato
    """
    service = get_onboarding_service()
    return service.complete_wizard(db, current_user.id)


@router.post("/skip", response_model=OnboardingStatusResponse)
async def skip_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Salta il wizard di onboarding
    
    Possibile solo se l'utente ha già almeno un edificio 
    (es. invitato da un altro utente).
    
    Returns:
        Status del wizard aggiornato
        
    Raises:
        400: Se l'utente non ha edifici
    """
    service = get_onboarding_service()
    
    try:
        return service.skip_wizard(db, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail="Non puoi saltare il wizard senza almeno un edificio"
        )


@router.post("/validate-device", response_model=OnboardingDeviceValidationResponse)
async def validate_device(
    validation_data: OnboardingDeviceValidation,
    current_user: User = Depends(get_current_user)
):
    """
    Valida un dispositivo tramite la ZCS API
    
    Verifica che il thing_key sia valido e il dispositivo sia raggiungibile.
    
    Args:
        validation_data: Thing key da validare
        
    Returns:
        Risultato validazione con info dispositivo se valido
    """
    service = get_onboarding_service()
    return await service.validate_device(validation_data.thing_key)


@router.get("/building", response_model=Optional[dict])
async def get_onboarding_building(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene l'edificio creato durante il wizard
    
    Returns:
        Dettagli edificio o null se non ancora creato
    """
    service = get_onboarding_service()
    status = service.get_status(db, current_user.id)
    
    if not status.building_id:
        return None
    
    from ....services.building_service import get_building_service
    building_service = get_building_service()
    
    building = building_service.get_building(db, status.building_id, current_user.id)
    
    if not building:
        return None
    
    return {
        "id": building.id,
        "name": building.name,
        "address": building.address,
        "latitude": building.latitude,
        "longitude": building.longitude
    }


@router.post("/reset", response_model=OnboardingStatusResponse)
async def reset_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resetta il wizard di onboarding (solo per debug/testing)
    
    ATTENZIONE: Non elimina edifici o dispositivi già creati.
    
    Returns:
        Status del wizard resettato
    """
    from ....models.building import UserOnboarding, OnboardingStatus
    
    onboarding = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == current_user.id
    ).first()
    
    if onboarding:
        onboarding.current_step = 1
        onboarding.status = OnboardingStatus.NOT_STARTED.value
        onboarding.step_data = {}
        onboarding.started_at = None
        onboarding.completed_at = None
        onboarding.building_id = None
        db.commit()
        db.refresh(onboarding)
    
    service = get_onboarding_service()
    return service.get_status(db, current_user.id)

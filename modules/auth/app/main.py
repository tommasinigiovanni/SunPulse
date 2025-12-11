"""
Auth Service - Validazione centralizzata token Auth0
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
from jose import jwt, JWTError
from functools import lru_cache
import os

app = FastAPI(
    title="SunPulse Auth Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "https://sunpulse-api")
ALGORITHMS = ["RS256"]

# Models
class TokenValidationRequest(BaseModel):
    token: str

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    error: Optional[str] = None

class UserInfo(BaseModel):
    user_id: str
    email: Optional[str]
    name: Optional[str]
    roles: List[str]
    permissions: List[str]

# JWKS Cache
_jwks_cache = {}

async def get_jwks():
    """Fetch Auth0 JWKS con cache"""
    if "keys" in _jwks_cache:
        return _jwks_cache["keys"]
    
    if not AUTH0_DOMAIN:
        return None
        
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        response.raise_for_status()
        _jwks_cache["keys"] = response.json()["keys"]
        return _jwks_cache["keys"]

def get_rsa_key(token: str, jwks: list) -> Optional[dict]:
    """Estrae RSA key dal JWKS per il token"""
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        return None
    
    for key in jwks:
        if key["kid"] == unverified_header.get("kid"):
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    return None

async def validate_token(token: str) -> TokenValidationResponse:
    """Valida token JWT Auth0"""
    
    # Dev mode: token mock
    if token == "mock-dev-token":
        return TokenValidationResponse(
            valid=True,
            user_id="mock-user-dev",
            email="dev@solardashboard.com",
            name="Sviluppatore",
            roles=["admin"],
            permissions=["read:devices", "write:devices", "read:analytics"]
        )
    
    if not AUTH0_DOMAIN:
        return TokenValidationResponse(valid=False, error="AUTH0_DOMAIN not configured")
    
    try:
        jwks = await get_jwks()
        if not jwks:
            return TokenValidationResponse(valid=False, error="Could not fetch JWKS")
        
        rsa_key = get_rsa_key(token, jwks)
        if not rsa_key:
            return TokenValidationResponse(valid=False, error="Invalid token key")
        
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return TokenValidationResponse(
            valid=True,
            user_id=payload.get("sub"),
            email=payload.get("email") or payload.get(f"https://{AUTH0_DOMAIN}/email"),
            name=payload.get("name") or payload.get(f"https://{AUTH0_DOMAIN}/name"),
            roles=payload.get("https://sunpulse/roles", []),
            permissions=payload.get("permissions", [])
        )
        
    except jwt.ExpiredSignatureError:
        return TokenValidationResponse(valid=False, error="Token expired")
    except jwt.JWTClaimsError:
        return TokenValidationResponse(valid=False, error="Invalid claims")
    except JWTError as e:
        return TokenValidationResponse(valid=False, error=f"JWT error: {str(e)}")
    except Exception as e:
        return TokenValidationResponse(valid=False, error=f"Validation error: {str(e)}")

# Dependency per altri servizi
async def get_current_user(authorization: str = Header(None)) -> UserInfo:
    """Dependency FastAPI per validazione token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.replace("Bearer ", "")
    result = await validate_token(token)
    
    if not result.valid:
        raise HTTPException(status_code=401, detail=result.error or "Invalid token")
    
    return UserInfo(
        user_id=result.user_id or "",
        email=result.email,
        name=result.name,
        roles=result.roles,
        permissions=result.permissions
    )

# Endpoints
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "auth",
        "auth0_configured": bool(AUTH0_DOMAIN)
    }

@app.post("/validate", response_model=TokenValidationResponse)
async def validate_token_endpoint(request: TokenValidationRequest):
    """Valida un token JWT Auth0"""
    return await validate_token(request.token)

@app.get("/me", response_model=UserInfo)
async def get_me(user: UserInfo = Depends(get_current_user)):
    """Ottieni info utente corrente dal token"""
    return user

@app.post("/check-permission")
async def check_permission(
    permission: str,
    user: UserInfo = Depends(get_current_user)
):
    """Verifica se utente ha un permesso specifico"""
    has_permission = permission in user.permissions or "admin" in user.roles
    return {
        "permission": permission,
        "granted": has_permission,
        "user_id": user.user_id
    }

@app.get("/jwks-status")
async def jwks_status():
    """Status cache JWKS"""
    return {
        "cached": "keys" in _jwks_cache,
        "keys_count": len(_jwks_cache.get("keys", []))
    }

@app.post("/clear-cache")
async def clear_cache():
    """Pulisce cache JWKS"""
    _jwks_cache.clear()
    return {"status": "cleared"}


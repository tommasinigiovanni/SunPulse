"""
JWT Authentication for Auth0
"""
import json
import httpx
from typing import Optional, Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel
import structlog

from ..config.settings import get_settings

logger = structlog.get_logger()

# Security scheme
security = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    """Token payload from Auth0"""
    sub: str  # User ID
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    # Auth0 returns aud as list when multiple audiences (API + userinfo)
    aud: Optional[str | list[str]] = None
    iss: Optional[str] = None
    permissions: list[str] = []
    roles: list[str] = []


class User(BaseModel):
    """Current user model"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    permissions: list[str] = []
    roles: list[str] = []
    is_admin: bool = False


# Cache per JWKS (JSON Web Key Set)
_jwks_cache: Dict[str, Any] = {}
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_TTL = timedelta(hours=1)


async def get_jwks(domain: str) -> Dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Auth0
    Cached for 1 hour
    """
    global _jwks_cache, _jwks_cache_time
    
    now = datetime.utcnow()
    
    # Use cache if valid
    if _jwks_cache and _jwks_cache_time and (now - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache
    
    try:
        jwks_url = f"https://{domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = now
            logger.info("JWKS fetched successfully", domain=domain)
            return _jwks_cache
    except Exception as e:
        logger.error("Failed to fetch JWKS", error=str(e), domain=domain)
        # Return cached if available, even if expired
        if _jwks_cache:
            return _jwks_cache
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch authentication keys"
        )


def get_signing_key(jwks: Dict[str, Any], token: str) -> Optional[str]:
    """
    Get the signing key from JWKS that matches the token's kid
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Construct RSA public key
                return key
        
        logger.warning("No matching key found in JWKS", kid=kid)
        return None
    except JWTError as e:
        logger.error("Error getting signing key", error=str(e))
        return None


async def verify_token(token: str) -> TokenPayload:
    """
    Verify and decode a JWT token from Auth0
    """
    settings = get_settings()
    domain = settings.AUTH0_DOMAIN
    
    try:
        # Get JWKS
        jwks = await get_jwks(domain)
        signing_key = get_signing_key(jwks, token)
        
        if not signing_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature"
            )
        
        # Decode and verify token
        # Use API audience (not client_id) for API authorization
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=f"https://{domain}/",
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        
        logger.debug("Token verified successfully", sub=payload.get("sub"))
        
        # Extract user info
        return TokenPayload(
            sub=payload.get("sub"),
            email=payload.get("email") or payload.get(f"https://sunpulse/email"),
            name=payload.get("name") or payload.get(f"https://sunpulse/name"),
            picture=payload.get("picture"),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            aud=payload.get("aud"),
            iss=payload.get("iss"),
            permissions=payload.get(f"https://sunpulse/permissions", []),
            roles=payload.get(f"https://sunpulse/roles", []),
        )
        
    except ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError as e:
        logger.warning("JWT validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Dependency: Get current authenticated user
    Raises 401 if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = await verify_token(token)
    
    user = User(
        id=payload.sub,
        email=payload.email,
        name=payload.name,
        picture=payload.picture,
        permissions=payload.permissions,
        roles=payload.roles,
        is_admin="admin" in payload.roles
    )
    
    logger.debug("User authenticated", user_id=user.id, email=user.email)
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency: Get current user if authenticated, None otherwise
    Does not raise error if not authenticated
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_auth(
    permissions: Optional[list[str]] = None,
    roles: Optional[list[str]] = None,
    any_of: bool = False
):
    """
    Decorator/dependency factory for requiring specific permissions/roles
    
    Args:
        permissions: List of required permissions
        roles: List of required roles
        any_of: If True, user needs ANY of the permissions/roles. If False, needs ALL.
    """
    async def check_permissions(user: User = Depends(get_current_user)) -> User:
        # Admin bypasses all checks
        if user.is_admin:
            return user
        
        required_perms = permissions or []
        required_roles = roles or []
        
        if any_of:
            # Check if user has ANY of the required permissions/roles
            has_permission = any(p in user.permissions for p in required_perms) if required_perms else True
            has_role = any(r in user.roles for r in required_roles) if required_roles else True
            
            if not (has_permission or has_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        else:
            # Check if user has ALL required permissions
            for perm in required_perms:
                if perm not in user.permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing permission: {perm}"
                    )
            
            # Check if user has ALL required roles
            for role in required_roles:
                if role not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing role: {role}"
                    )
        
        return user
    
    return check_permissions


class JWTBearer(HTTPBearer):
    """
    Custom JWT Bearer security scheme for route protection
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[User]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
            
            payload = await verify_token(credentials.credentials)
            return User(
                id=payload.sub,
                email=payload.email,
                name=payload.name,
                picture=payload.picture,
                permissions=payload.permissions,
                roles=payload.roles,
                is_admin="admin" in payload.roles
            )
        elif self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        return None

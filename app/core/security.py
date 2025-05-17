# File: app/core/security.py
# Description: Security utilities for JWT validation and role-based authorization

import time
from http import HTTPStatus
from typing import Annotated, Any, Dict, List, Optional

from fastapi import Depends, Header
from jose import JWTError, jwk, jwt

from app.core.config import settings
from app.core.exceptions import AppException, AuthException
from app.models.auth import JWTTokenData

# Cache for JWKS
_jwks_cache: Dict[str, Any] = {}
_jwks_last_updated: float = 0
_jwks_cache_ttl: int = 3600  # 1 hour


async def get_jwks() -> Dict[str, Any]:
    """
    Fetch the JWKS from the Keycloak server with caching

    Returns:
        JWKS dictionary

    Raises:
        AppException: If the JWKS cannot be fetched from the authentication server
    """
    global _jwks_cache, _jwks_last_updated

    # Check if we need to refresh the cache
    current_time = time.time()
    if not _jwks_cache or current_time - _jwks_last_updated > _jwks_cache_ttl:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.JWKS_URI)
                response.raise_for_status()

                _jwks_cache = response.json()
                _jwks_last_updated = current_time
        except Exception as e:
            raise AppException(
                message=f"Failed to fetch JWKS from authentication server",
                http_status=HTTPStatus.SERVICE_UNAVAILABLE
            )

    return _jwks_cache


def get_key_from_jwks(token: str, jwks: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get the key from JWKS that matches the token's key ID

    Args:
        token: JWT token
        jwks: JWKS dictionary

    Returns:
        Key dictionary or None if not found
    """
    try:
        # Get the header without verification
        header = jwt.get_unverified_header(token)

        # Find the key with matching kid
        for key in jwks.get("keys", []):
            if key.get("kid") == header.get("kid"):
                return key
    except JWTError:
        return None

    return None


async def validate_token(token: str) -> JWTTokenData:
    """
    Validate a JWT token using the JWKS from Keycloak

    Args:
        token: JWT token to validate

    Returns:
        Validated token data

    Raises:
        AuthException: If the token is invalid
    """
    if not token:
        raise AuthException(message="Missing authentication token")

    try:
        # Get JWKS
        jwks = await get_jwks()

        # Get the key for this token
        key = get_key_from_jwks(token, jwks)
        if not key:
            raise AuthException(message="Invalid token signature: Key not found")

        # Construct the public key
        public_key = jwk.construct(key)

        # Decode the token
        payload = jwt.decode(
            token,
            public_key.to_pem(),
            algorithms=["RS256"],  # Standard algorithm for JWT tokens
            options={"verify_aud": False}  # Skip audience validation
        )

        # Create token data model
        token_data = JWTTokenData(**payload)

        # Check if token is expired
        if token_data.exp < time.time():
            raise AuthException(message="Token has expired")

        return token_data

    except JWTError as e:
        raise AuthException(message=f"Invalid authentication token")
    except AuthException:
        # Re-raise AuthException without modification
        raise
    except Exception as e:
        raise AuthException(message=f"Error validating authentication token")


async def get_token_data(
    authorization: Optional[str] = Header(None)
) -> JWTTokenData:
    """
    Extract and validate the JWT token from the Authorization header

    Args:
        authorization: Authorization header value

    Returns:
        Validated token data

    Raises:
        AuthException: If the token is missing or invalid
    """
    if not authorization:
        raise AuthException(message="Missing authorization header")

    # Extract token from header (Bearer token)
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthException(message="Invalid authorization header format")

    token = parts[1]

    # Validate the token
    return await validate_token(token)


def has_role(required_role: str):
    """
    Dependency for checking if the user has a specific role

    Args:
        required_role: Role that is required for access

    Returns:
        Dependency function that checks the role
    """
    async def role_checker(
        token_data: JWTTokenData = Depends(get_token_data)
    ) -> JWTTokenData:
        if not token_data.has_role(required_role):
            # No logging here - will be logged by error handler
            raise AuthException(
                message=f"Access denied",
                http_status=HTTPStatus.FORBIDDEN
            )
        return token_data
    return role_checker

def has_any_role(required_roles: List[str]):
    """
    Dependency for checking if the user has any of the specified roles

    Args:
        required_roles: List of roles, any of which grants access

    Returns:
        Dependency function that checks the roles
    """
    async def role_checker(
        token_data: JWTTokenData = Depends(get_token_data)
    ) -> JWTTokenData:
        if not token_data.has_any_role(required_roles):
            # No logging here - will be logged by error handler
            roles_str = ", ".join(required_roles)
            raise AuthException(
                message=f"Access denied",
                http_status=HTTPStatus.FORBIDDEN
            )
        return token_data
    return role_checker


# Type annotation for token data dependency
TokenDataDep = Annotated[JWTTokenData, Depends(get_token_data)]

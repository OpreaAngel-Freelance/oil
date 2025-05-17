# File: app/models/auth.py
# Description: Authentication models for JWT validation

from typing import Dict, List, Optional

from sqlmodel import Field, SQLModel


class JWTTokenData(SQLModel):
    """JWT token data extracted from a validated token"""
    # Required fields
    sub: str = Field(description="Subject identifier (user ID)")
    exp: int = Field(description="Expiration time (Unix timestamp)")
    iat: int = Field(description="Issued at time (Unix timestamp)")

    # Fields from the provided token
    jti: str = Field(description="JWT ID")
    iss: str = Field(description="Issuer")
    typ: str = Field(description="Token type")
    azp: str = Field(description="Authorized party")
    sid: str = Field(description="Session ID")
    realm_access: Dict[str, List[str]] = Field(description="Realm-level roles")
    scope: str = Field(description="OAuth scopes")
    preferred_username: str = Field(description="Username")
    email: str = Field(description="Email address")

    # Optional fields that might be present in other tokens
    aud: Optional[List[str]] = Field(default=None, description="Audience")
    resource_access: Optional[Dict[str, Dict[str, List[str]]]] = Field(default=None, description="Resource-specific roles")

    @property
    def roles(self) -> List[str]:
        """Extract roles from the token"""
        roles = []

        # Add realm roles if available
        if self.realm_access and "roles" in self.realm_access:
            roles.extend(self.realm_access["roles"])

        # Add client-specific roles if available
        if self.resource_access:
            for client_roles in self.resource_access.values():
                if "roles" in client_roles:
                    roles.extend(client_roles["roles"])

        return roles

    def has_role(self, required_role: str) -> bool:
        """Check if the token has a specific role"""
        return required_role in self.roles

    def has_any_role(self, required_roles: List[str]) -> bool:
        """Check if the token has any of the required roles"""
        return any(role in self.roles for role in required_roles)

    def has_all_roles(self, required_roles: List[str]) -> bool:
        """Check if the token has all of the required roles"""
        return all(role in self.roles for role in required_roles)

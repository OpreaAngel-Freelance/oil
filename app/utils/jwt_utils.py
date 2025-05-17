# File: app/utils/jwt_utils.py
# Description: JWT utility functions

import logging
from typing import Dict, Any
from jose import jwt

# Initialize logger
logger = logging.getLogger(__name__)


def extract_token_header(token: str) -> Dict[str, Any]:
    """
    Extract the header from a JWT token without verification

    Args:
        token: JWT token

    Returns:
        Token header as a dictionary
    """
    return jwt.get_unverified_header(token)


def extract_token_payload(token: str) -> Dict[str, Any]:
    """
    Extract the payload from a JWT token without verification

    Args:
        token: JWT token

    Returns:
        Token payload as a dictionary
    """
    return jwt.get_unverified_claims(token)


def format_token_for_logging(token: str) -> str:
    """
    Format a token for logging (truncate to prevent sensitive data exposure)

    Args:
        token: JWT token

    Returns:
        Truncated token string safe for logging
    """
    if not token:
        return "<empty token>"

    parts = token.split('.')
    if len(parts) != 3:
        return "<invalid token format>"

    # Return only the first 10 characters of the token
    return f"{token[:10]}..."

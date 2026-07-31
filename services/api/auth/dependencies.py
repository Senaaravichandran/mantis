"""Authentication dependencies for FastAPI."""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Validate JWT and return user info.

    In development mode (AUTH_ENABLED=false), returns a mock user.
    In production, validates against Keycloak.
    """
    if not AUTH_ENABLED:
        return {
            "id": "dev-user-001",
            "email": "dev@mantis.local",
            "full_name": "Development User",
            "role": "admin",
        }

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    # TODO: Validate JWT against Keycloak
    # For now, accept any bearer token in auth-enabled mode
    return {
        "id": "authenticated-user",
        "email": "user@mantis.local",
        "full_name": "Authenticated User",
        "role": "engineer",
        "token": credentials.credentials,
    }


def require_role(role: str):
    """Dependency factory that requires a specific role."""
    async def check_role(user: dict = Depends(get_current_user)):
        if not AUTH_ENABLED:
            return user
        if user.get("role") != role and user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return user
    return check_role

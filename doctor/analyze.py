from __future__ import annotations

from docker import from_env

def connect():
    """Connect to the local Docker daemon using environment settings."""
    return from_env()

def system_df(client) -> dict:
    """Return Docker Engine /system/df data (same source as `docker system df`)."""
    return client.api.df()

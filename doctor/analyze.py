from __future__ import annotations

from docker import from_env
from docker.errors import DockerException

DOCKER_HELP = (
    "Docker Disk Doctor couldn't connect to the Docker daemon.\n\n"
    "Common fixes:\n"
    "  1) Make sure Docker is installed and running\n"
    "     - Try: docker ps\n\n"
    "  2) If you see Permission denied to /var/run/docker.sock, add your user to the docker group:\n"
    "     sudo usermod -aG docker $USER\n"
    "     (then log out and back in)\n\n"
    "  3) If you must run as root (not recommended), use the full path:\n"
    "     sudo ~/.local/bin/dockerdoctor\n"
)

def connect():
    """Connect to the local Docker daemon using environment settings."""
    try:
        return from_env()
    except DockerException as e:
        raise RuntimeError(DOCKER_HELP) from e

def system_df(client) -> dict:
    """Return Docker Engine /system/df data (same source as `docker system df`)."""
    try:
        return client.api.df()
    except DockerException as e:
        raise RuntimeError(DOCKER_HELP) from e

from __future__ import annotations

from docker.errors import APIError

def cleanup_unused_images(client, images: list[dict], apply: bool) -> tuple[int, int]:
    """Remove images marked unused by /system/df (Containers == 0). Safe-by-default."""
    to_remove = [i for i in images if not i["used"]]
    bytes_est = sum(i["size_bytes"] for i in to_remove)

    removed = 0
    if apply:
        for img in to_remove:
            try:
                client.images.remove(img["id"], force=False, prune_children=False)
                removed += 1
            except APIError:
                # If Docker refuses (still referenced), skip safely.
                continue

    return removed, bytes_est

def cleanup_orphan_volumes(client, volumes: list[dict], apply: bool) -> tuple[int, int]:
    """Remove volumes with RefCount == 0 (orphaned). Safe-by-default."""
    to_remove = [v for v in volumes if not v["attached"]]
    bytes_est = sum(v["size_bytes"] for v in to_remove)

    removed = 0
    if apply:
        for vol in to_remove:
            try:
                client.volumes.get(vol["name"]).remove(force=False)
                removed += 1
            except APIError:
                continue

    return removed, bytes_est

from __future__ import annotations

from docker.errors import APIError

def cleanup_unused_images(client, images: list[dict], apply: bool) -> tuple[int, int, int]:
    """Remove images marked unused by /system/df (Containers == 0)."""
    to_remove = [i for i in images if not i["used"]]
    bytes_est = sum(i["size_bytes"] for i in to_remove)

    removed = 0
    skipped = 0

    if apply:
        for img in to_remove:
            try:
                client.images.remove(img["id"], force=False)
                removed += 1
            except APIError:
                skipped += 1

    return removed, skipped, bytes_est

def cleanup_orphan_volumes(client, volumes: list[dict], apply: bool) -> tuple[int, int, int]:
    """Remove volumes with RefCount == 0 (orphaned)."""
    to_remove = [v for v in volumes if not v["attached"]]
    bytes_est = sum(v["size_bytes"] for v in to_remove)

    removed = 0
    skipped = 0

    if apply:
        for vol in to_remove:
            try:
                client.volumes.get(vol["name"]).remove(force=False)
                removed += 1
            except APIError:
                skipped += 1

    return removed, skipped, bytes_est

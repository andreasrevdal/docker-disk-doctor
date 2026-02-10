from __future__ import annotations

from doctor.utils import format_bytes

def analyze_containers(df: dict) -> list[dict]:
    containers = df.get("Containers", []) or []
    results: list[dict] = []

    for c in containers:
        names = c.get("Names") or []
        name = names[0].lstrip("/") if names else (c.get("Id", "")[:12])

        state = c.get("State", "unknown")

        size_rw = c.get("SizeRw", 0) or 0
        size_root = c.get("SizeRootFs", 0) or 0

        results.append({
            "name": name,
            "state": state,
            "size_rw_bytes": int(size_rw),
            "size_rw": format_bytes(size_rw),
            "size_rootfs_bytes": int(size_root),
            "size_rootfs": format_bytes(size_root),
        })

    results.sort(key=lambda x: x["size_rw_bytes"], reverse=True)
    return results

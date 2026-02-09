from __future__ import annotations

from doctor.utils import format_bytes

def analyze_volumes(df: dict) -> list[dict]:
    volumes = df.get("Volumes", []) or []
    results: list[dict] = []

    for v in volumes:
        usage = v.get("UsageData") or {}
        size = usage.get("Size", 0) or 0
        ref = usage.get("RefCount", 0) or 0

        results.append({
            "name": v.get("Name", ""),
            "driver": v.get("Driver", ""),
            "attached": int(ref) > 0,
            "refcount": int(ref),
            "size_bytes": int(size),
            "size": format_bytes(size),
        })

    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results

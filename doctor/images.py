from __future__ import annotations

from doctor.utils import format_bytes

def analyze_images(df: dict) -> list[dict]:
    images = df.get("Images", []) or []
    results: list[dict] = []

    for img in images:
        repo_tags = img.get("RepoTags") or ["<none>:<none>"]
        tag = repo_tags[0]

        used = (img.get("Containers", 0) or 0) > 0
        size = img.get("Size", 0) or 0
        reclaim = img.get("Reclaimable", 0) or 0

        results.append({
            "tag": tag,
            "id": (img.get("Id") or "")[:12],
            "used": used,
            "size_bytes": int(size),
            "size": format_bytes(size),
            "reclaimable_bytes": int(reclaim),
            "reclaimable": format_bytes(reclaim),
        })

    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results

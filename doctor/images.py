from doctor.utils import format_bytes

def analyze_images(df):
    results = []
    for img in df.get("Images", []):
        used = (img.get("Containers", 0) or 0) > 0
        size = img.get("Size", 0) or 0
        reclaim = img.get("Reclaimable", 0) or 0
        tag = (img.get("RepoTags") or ["<none>:<none>"])[0]
        results.append({
            "tag": tag,
            "id": (img.get("Id") or "")[:12],
            "used": used,
            "size_bytes": size,
            "size": format_bytes(size),
            "reclaimable_bytes": reclaim,
            "reclaimable": format_bytes(reclaim),
        })
    return sorted(results, key=lambda x: x["size_bytes"], reverse=True)

from doctor.utils import format_bytes

def analyze_images(df: dict):
    images = df.get("Images", [])
    results = []

    for img in images:
        repo_tags = img.get("RepoTags") or ["<none>:<none>"]
        tag = repo_tags[0]
        used = (img.get("Containers", 0) or 0) > 0

        results.append({
            "tag": tag,
            "id": (img.get("Id") or "")[:12],
            "used": used,
            "size_bytes": img.get("Size", 0) or 0,
            "size": format_bytes(img.get("Size", 0) or 0),
            "reclaimable_bytes": img.get("Reclaimable", 0) or 0,
            "reclaimable": format_bytes(img.get("Reclaimable", 0) or 0),
        })

    # Sort biggest first
    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results

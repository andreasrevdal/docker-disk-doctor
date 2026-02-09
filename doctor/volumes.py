from doctor.utils import format_bytes

def analyze_volumes(df: dict):
    volumes = df.get("Volumes", [])
    results = []

    for v in volumes:
        usage = v.get("UsageData") or {}
        size = usage.get("Size", 0) or 0
        ref = usage.get("RefCount", 0) or 0

        results.append({
            "name": v.get("Name", ""),
            "driver": v.get("Driver", ""),
            "attached": ref > 0,
            "refcount": ref,
            "size_bytes": size,
            "size": format_bytes(size),
        })

    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results

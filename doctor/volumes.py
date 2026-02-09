from doctor.utils import format_bytes

def analyze_volumes(df):
    results = []
    for v in df.get("Volumes", []):
        usage = v.get("UsageData") or {}
        size = usage.get("Size", 0) or 0
        ref = usage.get("RefCount", 0) or 0
        results.append({
            "name": v.get("Name"),
            "attached": ref > 0,
            "refcount": ref,
            "size_bytes": size,
            "size": format_bytes(size),
        })
    return results

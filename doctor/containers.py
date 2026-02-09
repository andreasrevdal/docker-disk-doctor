from doctor.utils import format_bytes

def analyze_containers(df):
    results = []
    for c in df.get("Containers", []):
        rw = c.get("SizeRw", 0) or 0
        root = c.get("SizeRootFs", 0) or 0
        name = (c.get("Names") or [""])[0].lstrip("/")
        results.append({
            "name": name,
            "state": c.get("State", ""),
            "size_rw_bytes": rw,
            "size_rw": format_bytes(rw),
            "size_rootfs": format_bytes(root),
        })
    return results

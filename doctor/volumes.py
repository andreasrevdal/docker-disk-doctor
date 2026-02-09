def analyze_volumes(client):
    volumes = client.volumes.list()
    results = []
    for v in volumes:
        results.append({
            "name": v.name,
            "driver": v.attrs.get("Driver")
        })
    return results

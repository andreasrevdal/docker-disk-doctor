def analyze_containers(client):
    containers = client.containers.list(all=True)
    results = []
    for c in containers:
        results.append({
            "name": c.name,
            "status": c.status,
            "id": c.short_id
        })
    return results

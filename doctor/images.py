def analyze_images(client):
    images = client.images.list()
    results = []
    for img in images:
        results.append({
            "id": img.short_id,
            "size": img.attrs.get("Size", 0),
            "tags": img.tags or ["<none>"]
        })
    return results

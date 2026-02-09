from docker.errors import APIError

def cleanup_unused_images(client, images, apply):
    removed = 0
    est = 0
    for img in images:
        if img["used"]:
            continue
        est += img["size_bytes"]
        if apply:
            try:
                client.images.remove(img["id"])
                removed += 1
            except APIError:
                pass
    return removed, est

def cleanup_orphan_volumes(client, volumes, apply):
    removed = 0
    est = 0
    for v in volumes:
        if v["attached"]:
            continue
        est += v["size_bytes"]
        if apply:
            try:
                client.volumes.get(v["name"]).remove()
                removed += 1
            except APIError:
                pass
    return removed, est

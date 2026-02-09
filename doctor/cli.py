from doctor.analyze import connect
from doctor.images import analyze_images
from doctor.containers import analyze_containers
from doctor.volumes import analyze_volumes
from rich.console import Console

console = Console()

def main():
    console.print("[bold green]Docker Disk Doctor[/bold green]")
    client = connect()

    images = analyze_images(client)
    containers = analyze_containers(client)
    volumes = analyze_volumes(client)

    console.print(f"Images: {len(images)}")
    console.print(f"Containers: {len(containers)}")
    console.print(f"Volumes: {len(volumes)}")

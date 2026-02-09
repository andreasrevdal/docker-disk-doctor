import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from doctor.analyze import connect, system_df
from doctor.images import analyze_images
from doctor.containers import analyze_containers
from doctor.volumes import analyze_volumes
from doctor.cleanup import cleanup_unused_images, cleanup_orphan_volumes
from doctor.utils import format_bytes

console = Console()

def main():
    parser = argparse.ArgumentParser(prog="docker-disk-doctor")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    client = connect()
    df = system_df(client)

    images = analyze_images(df)
    containers = analyze_containers(df)
    volumes = analyze_volumes(df)

    console.print(Panel(
        f"Images: {len(images)}\nContainers: {len(containers)}\nVolumes: {len(volumes)}",
        title="Docker Disk Doctor"
    ))

    if args.clean:
        if args.apply and not args.yes:
            console.print("Refusing to apply without --yes")
            return
        if args.all:
            ri, ei = cleanup_unused_images(client, images, args.apply)
            rv, ev = cleanup_orphan_volumes(client, volumes, args.apply)
            console.print(f"Images freed: {format_bytes(ei)}")
            console.print(f"Volumes freed: {format_bytes(ev)}")

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


def summary_panel(images, containers, volumes):
    used_images = sum(1 for i in images if i["used"])
    unused_images = len(images) - used_images

    running = sum(1 for c in containers if c["state"] == "running")
    stopped = len(containers) - running

    attached = sum(1 for v in volumes if v["attached"])
    orphaned = len(volumes) - attached

    total_images = sum(i["size_bytes"] for i in images)
    total_rw = sum(c["size_rw_bytes"] for c in containers)
    total_volumes = sum(v["size_bytes"] for v in volumes)

    text = "\n".join([
        f"Images     : {len(images)} (used {used_images} / unused {unused_images}) — {format_bytes(total_images)}",
        f"Containers : {len(containers)} (running {running} / stopped {stopped}) — writable {format_bytes(total_rw)}",
        f"Volumes    : {len(volumes)} (attached {attached} / orphaned {orphaned}) — {format_bytes(total_volumes)}",
        "",
        "Note: Tool is safe-by-default. Nothing is deleted automatically."
    ])

    return Panel(text, title="Docker Disk Doctor", expand=False)


def images_table(images):
    table = Table(title="Images (used vs unused)")
    table.add_column("Tag", overflow="fold")
    table.add_column("Status")
    table.add_column("Size", justify="right")

    for img in images[:30]:
        status = "[green]used[/green]" if img["used"] else "[yellow]unused[/yellow]"
        table.add_row(img["tag"], status, img["size"])

    return table


def containers_table(containers):
    table = Table(title="Containers (running vs stopped)")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Writable", justify="right")
    table.add_column("RootFS", justify="right")

    for c in containers:
        state = "[green]running[/green]" if c["state"] == "running" else "[yellow]stopped[/yellow]"
        table.add_row(c["name"], state, c["size_rw"], c["size_rootfs"])

    return table


def volumes_table(volumes):
    table = Table(title="Volumes (attached vs orphaned)")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Size", justify="right")

    for v in volumes:
        status = "[green]attached[/green]" if v["attached"] else "[yellow]orphaned[/yellow]"
        table.add_row(v["name"], status, v["size"])

    return table


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

    console.print(summary_panel(images, containers, volumes))
    console.print()
    console.print(images_table(images))
    console.print()
    console.print(containers_table(containers))
    console.print()
    console.print(volumes_table(volumes))

    if args.clean:
        if args.apply and not args.yes:
            console.print("\n[red]Refusing to delete without --yes[/red]")
            return

        if args.all:
            img_removed, img_bytes = cleanup_unused_images(client, images, args.apply)
            vol_removed, vol_bytes = cleanup_orphan_volumes(client, volumes, args.apply)

            console.print("\n[bold]Cleanup result[/bold]")
            console.print(f"Unused images: {'removed' if args.apply else 'would remove'} — {format_bytes(img_bytes)}")
            console.print(f"Orphan volumes: {'removed' if args.apply else 'would remove'} — {format_bytes(vol_bytes)}")

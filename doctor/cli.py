from __future__ import annotations

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

def _summary_panel(images: list[dict], containers: list[dict], volumes: list[dict]) -> Panel:
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

def _images_table(images: list[dict]) -> Table:
    t = Table(title="Images (used vs unused)")
    t.add_column("Tag", overflow="fold")
    t.add_column("Status")
    t.add_column("Size", justify="right")
    t.add_column("Reclaimable", justify="right")

    for i in images[:30]:
        status = "[green]used[/green]" if i["used"] else "[yellow]unused[/yellow]"
        t.add_row(i["tag"], status, i["size"], i["reclaimable"])
    return t

def _containers_table(containers: list[dict]) -> Table:
    t = Table(title="Containers (running vs stopped)")
    t.add_column("Name", overflow="fold")
    t.add_column("State")
    t.add_column("Writable", justify="right")
    t.add_column("RootFS", justify="right")

    for c in containers[:30]:
        state = "[green]running[/green]" if c["state"] == "running" else "[yellow]stopped[/yellow]"
        t.add_row(c["name"], state, c["size_rw"], c["size_rootfs"])
    return t

def _volumes_table(volumes: list[dict]) -> Table:
    t = Table(title="Volumes (attached vs orphaned)")
    t.add_column("Name", overflow="fold")
    t.add_column("Status")
    t.add_column("Size", justify="right")
    t.add_column("RefCount", justify="right")

    for v in volumes[:30]:
        status = "[green]attached[/green]" if v["attached"] else "[yellow]orphaned[/yellow]"
        t.add_row(v["name"], status, v["size"], str(v["refcount"]))
    return t

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="docker-disk-doctor",
        description="Explain-first Docker disk usage inspector (safe-by-default)."
    )
    p.add_argument("--clean", action="store_true", help="Show what would be removed (dry-run).")
    p.add_argument("--apply", action="store_true", help="Actually perform removals (requires --yes).")
    p.add_argument("--yes", action="store_true", help="Confirm destructive actions when using --apply.")
    p.add_argument("--images", action="store_true", help="Include unused image cleanup.")
    p.add_argument("--volumes", action="store_true", help="Include orphan volume cleanup.")
    p.add_argument("--all", action="store_true", help="Equivalent to --images --volumes.")
    return p

def main():
    args = _build_parser().parse_args()

    client = connect()
    df = system_df(client)

    images = analyze_images(df)
    containers = analyze_containers(df)
    volumes = analyze_volumes(df)

    console.print(_summary_panel(images, containers, volumes))
    console.print()
    console.print(_images_table(images))
    console.print()
    console.print(_containers_table(containers))
    console.print()
    console.print(_volumes_table(volumes))

    if args.clean or args.apply:
        do_images = args.all or args.images
        do_volumes = args.all or args.volumes

        if args.apply and not args.yes:
            console.print("\n[bold red]Refusing to delete without --yes.[/bold red]")
            console.print("[dim]Tip: run with --clean first, then add --apply --yes when you’re confident.[/dim]")
            return

        if not do_images and not do_volumes:
            console.print("\n[yellow]Nothing selected.[/yellow] Use --all or --images/--volumes.")
            return

        console.print("\n[bold]Cleanup plan[/bold]")
        console.print("[dim]Dry-run unless you pass --apply --yes.[/dim]\n")

        total_est = 0

        if do_images:
            removed, bytes_est = cleanup_unused_images(client, images, apply=args.apply)
            total_est += bytes_est
            console.print(f"- Unused images: {'removed '+str(removed) if args.apply else 'would remove'} (est {format_bytes(bytes_est)})")

        if do_volumes:
            removed, bytes_est = cleanup_orphan_volumes(client, volumes, apply=args.apply)
            total_est += bytes_est
            console.print(f"- Orphan volumes: {'removed '+str(removed) if args.apply else 'would remove'} (est {format_bytes(bytes_est)})")

        console.print(f"\n[bold]Estimated space change:[/bold] {format_bytes(total_est)}")
        if args.apply:
            console.print("[green]Cleanup completed.[/green]")
        else:
            console.print("[yellow]Dry-run only.[/yellow] Re-run with --apply --yes to actually delete.")

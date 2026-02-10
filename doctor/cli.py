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

def _load():
    client = connect()
    df = system_df(client)
    images = analyze_images(df)
    containers = analyze_containers(df)
    volumes = analyze_volumes(df)
    return client, images, containers, volumes

def cmd_report(_args):
    _client, images, containers, volumes = _load()
    console.print(_summary_panel(images, containers, volumes))
    console.print()
    console.print(_images_table(images))
    console.print()
    console.print(_containers_table(containers))
    console.print()
    console.print(_volumes_table(volumes))

def _do_cleanup(target: str, apply: bool, yes: bool):
    client, images, containers, volumes = _load()

    console.print(_summary_panel(images, containers, volumes))
    console.print()

    do_images = target in ("images", "all")
    do_volumes = target in ("volumes", "all")

    if apply and not yes:
        console.print("[bold red]Refusing to delete without --yes.[/bold red]")
        console.print("[dim]Tip: run `dockerdoctor test clean all` first, then re-run with --yes.[/dim]")
        return 2

    console.print("[bold]Cleanup plan[/bold]")
    console.print("[dim]Dry-run unless you use `dockerdoctor clean ... --yes`.[/dim]\n")

    total_est = 0

    if do_images:
        removed, skipped, est = cleanup_unused_images(client, images, apply=apply)
        total_est += est
        if apply:
            console.print(f"- Unused images: removed {removed}, skipped {skipped} (est {format_bytes(est)})")
        else:
            console.print(f"- Unused images: would remove {sum(1 for i in images if not i['used'])} (est {format_bytes(est)})")

    if do_volumes:
        removed, skipped, est = cleanup_orphan_volumes(client, volumes, apply=apply)
        total_est += est
        if apply:
            console.print(f"- Orphan volumes: removed {removed}, skipped {skipped} (est {format_bytes(est)})")
        else:
            console.print(f"- Orphan volumes: would remove {sum(1 for v in volumes if not v['attached'])} (est {format_bytes(est)})")

    console.print(f"\n[bold]Estimated space change:[/bold] {format_bytes(total_est)}")
    if apply:
        console.print("[green]Cleanup completed.[/green]")
    else:
        console.print("[yellow]Dry-run only.[/yellow]")

    return 0

def cmd_test_clean(args):
    return _do_cleanup(args.target, apply=False, yes=False)

def cmd_clean(args):
    return _do_cleanup(args.target, apply=True, yes=args.yes)

def build_parser():
    p = argparse.ArgumentParser(prog="dockerdoctor", description="Docker Disk Doctor (safe-by-default)")
    sub = p.add_subparsers(dest="command")

    report = sub.add_parser("report", help="Show disk usage breakdown (default).")
    report.set_defaults(func=cmd_report)

    test = sub.add_parser("test", help="Dry-run actions.")
    test_sub = test.add_subparsers(dest="test_command")

    test_clean = test_sub.add_parser("clean", help="Dry-run cleanup plan.")
    test_clean.add_argument("target", choices=["images", "volumes", "all"], help="What to clean.")
    test_clean.set_defaults(func=cmd_test_clean)

    clean = sub.add_parser("clean", help="Apply cleanup (requires --yes).")
    clean.add_argument("target", choices=["images", "volumes", "all"], help="What to clean.")
    clean.add_argument("--yes", action="store_true", help="Confirm destructive actions.")
    clean.set_defaults(func=cmd_clean)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if not getattr(args, "command", None):
            cmd_report(args)
            return 0
        res = args.func(args)
        return int(res) if isinstance(res, int) else 0
    except RuntimeError as e:
        console.print(Panel(str(e), title="Docker connection error", style="red", expand=False))
        return 1

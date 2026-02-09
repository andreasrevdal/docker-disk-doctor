from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from doctor.analyze import connect, system_df
from doctor.images import analyze_images
from doctor.containers import analyze_containers
from doctor.volumes import analyze_volumes
from doctor.utils import format_bytes

console = Console()

def _summary_panel(images, containers, volumes, df: dict) -> Panel:
    used_images = sum(1 for i in images if i["used"])
    unused_images = len(images) - used_images

    running = sum(1 for c in containers if c["state"] == "running")
    stopped = len(containers) - running

    attached = sum(1 for v in volumes if v["attached"])
    orphaned = len(volumes) - attached

    total_images_size = sum(i["size_bytes"] for i in images)
    total_cont_rw = sum(c["size_rw_bytes"] for c in containers)
    total_vol_size = sum(v["size_bytes"] for v in volumes)

    # “Reclaimable” isn’t perfect, but Docker provides it for images/cache.
    reclaim_images = sum(i["reclaimable_bytes"] for i in images)

    buildcache = df.get("BuildCache", []) or []
    reclaim_cache = sum((bc.get("Size", 0) or 0) for bc in buildcache if not bc.get("InUse", False))

    text = "\n".join([
        f"[bold]Images[/bold]     : {len(images)}  (used {used_images} / unused {unused_images})  — {format_bytes(total_images_size)}",
        f"[bold]Containers[/bold] : {len(containers)}  (running {running} / stopped {stopped}) — writable {format_bytes(total_cont_rw)}",
        f"[bold]Volumes[/bold]    : {len(volumes)}  (attached {attached} / orphaned {orphaned}) — {format_bytes(total_vol_size)}",
        "",
        f"[bold]Reclaimable (estimate)[/bold] : images {format_bytes(reclaim_images)} + build cache {format_bytes(reclaim_cache)}",
        "[dim]Note: Tool is read-only. Nothing is deleted automatically.[/dim]"
    ])
    return Panel(text, title="Docker Disk Doctor", expand=False)

def _images_table(images) -> Table:
    t = Table(title="Images (used vs unused)", show_lines=False)
    t.add_column("Tag", overflow="fold")
    t.add_column("Used")
    t.add_column("Size", justify="right")
    t.add_column("Reclaimable", justify="right")

    for i in images[:30]:  # top 30 to keep output readable
        used = "[green]used[/green]" if i["used"] else "[yellow]unused[/yellow]"
        t.add_row(i["tag"], used, i["size"], i["reclaimable"])

    return t

def _containers_table(containers) -> Table:
    t = Table(title="Containers (running vs stopped)", show_lines=False)
    t.add_column("Name", overflow="fold")
    t.add_column("State")
    t.add_column("Writable", justify="right")
    t.add_column("RootFS", justify="right")

    for c in containers[:30]:
        state = "[green]running[/green]" if c["state"] == "running" else "[yellow]stopped[/yellow]"
        t.add_row(c["name"], state, c["size_rw"], c["size_rootfs"])

    return t

def _volumes_table(volumes) -> Table:
    t = Table(title="Volumes (attached vs orphaned)", show_lines=False)
    t.add_column("Name", overflow="fold")
    t.add_column("Attached")
    t.add_column("Size", justify="right")
    t.add_column("RefCount", justify="right")

    for v in volumes[:30]:
        attached = "[green]attached[/green]" if v["attached"] else "[yellow]orphaned[/yellow]"
        t.add_row(v["name"], attached, v["size"], str(v["refcount"]))

    return t

def main():
    client = connect()
    df = system_df(client)

    images = analyze_images(df)
    containers = analyze_containers(df)
    volumes = analyze_volumes(df)

    console.print(_summary_panel(images, containers, volumes, df))
    console.print()
    console.print(_images_table(images))
    console.print()
    console.print(_containers_table(containers))
    console.print()
    console.print(_volumes_table(volumes))

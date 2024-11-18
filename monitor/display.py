"""Display module for system monitor."""
from datetime import datetime
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from rich.align import Align
from rich.live import Live
from rich.text import Text
from textwrap import fill

console = Console()

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} TB"

def get_status_color(value: float, threshold_type: str) -> str:
    """Get color based on threshold."""
    thresholds = {
        'cpu': {'warning': 70, 'critical': 90},
        'memory': {'warning': 70, 'critical': 90},
        'disk': {'warning': 80, 'critical': 95}
    }.get(threshold_type, {'warning': 70, 'critical': 90})
    
    if value >= thresholds['critical']:
        return "red"
    elif value >= thresholds['warning']:
        return "yellow"
    return "green"

def create_metrics_panel(metrics: dict) -> Panel:
    """Creates a panel with system metrics."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column(style="blue")
    table.add_column(style="green")
    
    # CPU metrics
    cpu = metrics.get('cpu', {})
    cpu_color = get_status_color(cpu.get('usage', 0), 'cpu')
    table.add_row(
        "CPU Usage:",
        f"[{cpu_color}]{cpu.get('usage', 0):.1f}%[/{cpu_color}]"
    )
    table.add_row(
        "CPU Frequency:",
        f"{cpu.get('frequency', 0):.1f} MHz"
    )
    
    # Memory metrics
    mem = metrics.get('memory', {})
    mem_color = get_status_color(mem.get('percent', 0), 'memory')
    table.add_row(
        "Memory Usage:",
        f"[{mem_color}]{mem.get('percent', 0):.1f}%[/{mem_color}]"
    )
    table.add_row(
        "Memory Total:",
        f"{format_bytes(mem.get('total', 0))}"
    )
    
    # Disk metrics
    disk = metrics.get('disk', {})
    disk_color = get_status_color(disk.get('percent', 0), 'disk')
    table.add_row(
        "Disk Usage:",
        f"[{disk_color}]{disk.get('percent', 0):.1f}%[/{disk_color}]"
    )
    table.add_row(
        "Disk I/O:",
        f"↑{format_bytes(disk.get('write_bytes', 0))} ↓{format_bytes(disk.get('read_bytes', 0))}"
    )
    
    return Panel(
        Align.center(table),
        title="[bold blue]System Metrics[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def create_services_panel(services: list) -> Panel:
    """Creates a panel with problematic services status."""
    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Service", style="blue")
    table.add_column("Status", justify="center")
    table.add_column("Details", justify="right")
    
    status_colors = {
        'failed': '[red]Failed[/red]',
        'inactive': '[yellow]Inactive[/yellow]',
        'error': '[red]Error[/red]',
        'dead': '[red]Dead[/red]',
        'unknown': '[yellow]Unknown[/yellow]'
    }
    
    if not services:
        table.add_row(
            "No issues",
            "[green]All services OK[/green]",
            ""
        )
    else:
        for service in services:
            name = service.get('name', 'Unknown').replace('.service', '')
            status = service.get('status', 'unknown').lower()
            sub_status = service.get('sub_status', '')
            load_status = service.get('load_status', '')
            
            status_display = status_colors.get(status, f'[yellow]{status}[/yellow]')
            details = f"{load_status}/{sub_status}" if load_status and sub_status else "No details"
            
            table.add_row(name, status_display, details)
    
    return Panel(
        Align.center(table),
        title="[bold blue]Problem Services[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def create_mount_points_panel(mount_points: list) -> Panel:
    """Creates a panel with mount points status."""
    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    table.add_column("Device", style="blue")
    table.add_column("Mount Point", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Usage", justify="right")
    table.add_column("Status", justify="center")
    
    if not mount_points:
        table.add_row(
            "No mount points available",
            "",
            "",
            "",
            "[yellow]N/A[/yellow]"
        )
        return Panel(
            table,
            title="[bold blue]Mount Points Status[/bold blue]",
            border_style="blue",
            padding=(1, 1)
        )
    
    for mp in mount_points:
        if not isinstance(mp, dict):
            continue
            
        if 'error' in mp and not isinstance(mp.get('error'), str):
            continue
            
        status_color = get_status_color(mp.get('percent', 0), 'disk')
        status = '[green]OK[/green]' if mp.get('status') == 'mounted' else f'[red]Error: {mp.get("error", "Unknown")}[/red]'
        
        usage = (
            f'[{status_color}]{mp.get("percent", 0):.1f}%[/{status_color}]'
            if mp.get('status') == 'mounted'
            else 'N/A'
        )
        
        table.add_row(
            mp.get('device', 'Unknown'),
            mp.get('mountpoint', 'Unknown'),
            mp.get('fstype', 'Unknown'),
            usage,
            status
        )
    
    return Panel(
        table,
        title="[bold blue]Mount Points Status[/bold blue]",
        border_style="blue",
        padding=(1, 1)
    )

def create_partition_panel(partition_data: dict, partition_name: str) -> Panel:
    """Creates a panel for partition information."""
    if not partition_data or "error" in partition_data:
        return Panel(
            Text(str(partition_data.get("error", "Failed to get partition data")), style="red"),
            title=f"[bold blue]{partition_name}[/bold blue]",
            border_style="blue",
            padding=(1, 1)
        )
    
    text = Text()
    for package_name, items in partition_data.items():
        text.append(f"{package_name}:\n", style="bold blue")
        for item in items:
            text.append(f"  {item.get('name', 'Unknown')}\n", style="cyan")
            text.append(f"  Size: {item.get('size', 0)} bytes\n", style="magenta")
            text.append(f"  Date: {item.get('date', 'Unknown')}\n", style="yellow")
            text.append(f"  Status: {item.get('status', 'unknown')}\n", style="green")
            text.append(f"  Valid: {item.get('valid', False)}\n", style="green" if item.get('valid', False) else "red")
            text.append("\n")
    
    return Panel(
        text,
        title=f"[bold blue]{partition_name}[/bold blue]",
        border_style="blue",
        padding=(1, 1)
    )

def create_system_logs_panel(logs: list) -> Panel:
    """Creates a panel for system logs from journalctl."""
    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    table.add_column("Time", style="dim", width=8)
    table.add_column("Level", width=8)
    table.add_column("Message")
    
    if not logs:
        table.add_row("--:--:--", "[yellow]INFO[/yellow]", "No logs available")
        return Panel(table, title="[bold blue]System Logs (Errors & Failures)[/bold blue]",
                    border_style="blue", padding=(1, 1))
    
    for log in logs:
        if not isinstance(log, dict):
            continue
            
        level = log.get('level', 'INFO').upper()
        color = {
            'ERROR': 'red',
            'WARNING': 'yellow',
            'INFO': 'green',
            'DEBUG': 'blue'
        }.get(level, 'white')
        
        time_str = log.get('timestamp', datetime.now()).strftime('%H:%M:%S')
        message = log.get('message', 'No message')
        wrapped_message = fill(message, width=100, break_long_words=False, replace_whitespace=False)
        
        table.add_row(
            time_str,
            f"[{color}]{level}[/{color}]",
            wrapped_message
        )
    
    return Panel(
        table,
        title="[bold blue]System Logs (Errors & Failures)[/bold blue]",
        border_style="blue",
        padding=(1, 1)
    )

def create_dashboard(metrics: dict) -> Layout:
    """Creates the dashboard layout with system metrics and logs."""
    if not isinstance(metrics, dict):
        metrics = {}
        
    layout = Layout()
    
    # Split into header, body, and footer
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    # Create header
    current_time = datetime.fromtimestamp(metrics.get('timestamp', time.time())).strftime('%H:%M:%S')
    title = f"[bold white on blue] System Monitor [/bold white on blue] [bold blue]{current_time}[/bold blue]"
    layout["header"].update(Align.center(title, vertical="middle"))
    
    # Split body into sections
    layout["body"].split(
        Layout(name="upper"),
        Layout(name="middle", size=30),
        Layout(name="lower", size=20)
    )
    
    # Split upper section for metrics, services, and mount points
    layout["body"]["upper"].split_row(
        Layout(name="metrics"),
        Layout(name="services"),
        Layout(name="mount_points")
    )
    
    # Split middle section for partition information
    layout["body"]["middle"].split_row(
        Layout(name="partition1"),
        Layout(name="partition2"),
        Layout(name="partition3")
    )
    
    # Update upper panels
    layout["body"]["upper"]["metrics"].update(create_metrics_panel(metrics))
    layout["body"]["upper"]["services"].update(create_services_panel(metrics.get('services', [])))
    layout["body"]["upper"]["mount_points"].update(create_mount_points_panel(metrics.get('mount_points', [])))
    
    # Update partition panels
    partitions_data = metrics.get('partitions', {})
    layout["body"]["middle"]["partition1"].update(create_partition_panel(partitions_data.get('partition1', {}), "Partition 1"))
    layout["body"]["middle"]["partition2"].update(create_partition_panel(partitions_data.get('partition2', {}), "Partition 2"))
    layout["body"]["middle"]["partition3"].update(create_partition_panel(partitions_data.get('partition3', {}), "Partition 3"))
    
    # Update system logs panel
    layout["body"]["lower"].update(create_system_logs_panel(metrics.get('logs', [])))
    
    # Add footer with help text
    footer_text = "[dim]Press Ctrl+C to exit | Updated every 2s[/dim]"
    layout["footer"].update(Align.center(footer_text))
    
    return layout
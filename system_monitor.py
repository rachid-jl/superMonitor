"""Main system monitor script."""
import sys
import signal
import time
from rich.live import Live
from rich.console import Console
from monitor import MetricsCollector, create_dashboard, REFRESH_RATE

def signal_handler(sig, frame):
    """Handle cleanup on exit."""
    print("\nGracefully shutting down...")
    sys.exit(0)

def main():
    """Main monitoring loop."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    console = Console()
    
    try:
        metrics_collector = MetricsCollector()
    except Exception as e:
        console.print(f"[red]Failed to initialize metrics collector: {str(e)}[/red]")
        return 1
    
    try:
        with Live(auto_refresh=False) as live:
            while True:
                try:
                    metrics = metrics_collector.get_metrics()
                    dashboard = create_dashboard(metrics)
                    live.update(dashboard, refresh=True)
                except Exception as e:
                    console.print(f"[red]Error updating dashboard: {str(e)}[/red]")
                finally:
                    time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        return 1
    finally:
        if 'metrics_collector' in locals():
            metrics_collector.__del__()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
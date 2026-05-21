import time
import sys
from rich.live import Live
from ui.dashboard import DashboardManager

def main():
    """
    Main entry point for the Command Center UI.
    Connects to Redis telemetry and updates the dashboard in real-time.
    """
    dashboard = DashboardManager()
    
    try:
        # Using Rich Live to render the layout with 10 refreshes per second
        with Live(dashboard.render(), refresh_per_second=10, screen=True) as live:
            dashboard.add_log("Dashboard initialized.")
            dashboard.add_log("Listening for telemetry signals...")
            
            # Real-time polling loop
            while True:
                # 1. Fetch live telemetry data from Redis
                dashboard.fetch_telemetry()
                
                # 2. Re-render the dashboard layout with new data
                live.update(dashboard.render())
                
                # 3. Micro-sleep to keep CPU usage low
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        print("\n[bold red]Command Center shutting down...[/bold red]")
        sys.exit(0)
    except Exception as e:
        print(f"Critical UI Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

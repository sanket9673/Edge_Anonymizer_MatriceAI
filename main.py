import time
import sys
from rich.live import Live
from ui.dashboard import DashboardManager

def main():
    dashboard = DashboardManager()
    
    try:
        with Live(dashboard.render(), refresh_per_second=4, screen=True) as live:
            # Simulate Redis connection
            time.sleep(1.5)
            dashboard.update_status("Redis Broker", "[bold green]Online[/bold green]")
            dashboard.add_log("Redis Broker heartbeat detected.")
            live.update(dashboard.render())
            
            # Simulate Ingress startup
            time.sleep(1.5)
            dashboard.update_status("Ingress Gateway", "[bold green]Online[/bold green]")
            dashboard.add_log("Ingress Gateway listening on camera stream.")
            live.update(dashboard.render())
            
            # Simulate AI Model loading
            time.sleep(1.5)
            dashboard.update_status("AI Processor", "[bold green]Online[/bold green]")
            dashboard.add_log("YOLOv8 model weights loaded successfully.")
            live.update(dashboard.render())
            
            dashboard.add_log("System fully operational.")
            live.update(dashboard.render())
            
            # Keep the UI running
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        # Graceful exit
        print("\n[bold red]System shutting down...[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()

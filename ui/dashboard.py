from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from rich.align import Align
from datetime import datetime
import redis
import json
from ingress.config import REDIS_HOST, REDIS_PORT

class DashboardManager:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.statuses = {
            "Ingress Gateway": "[bold red]Offline[/bold red]",
            "AI Processor": "[bold red]Offline[/bold red]",
            "Redis Broker": "[bold red]Offline[/bold red]"
        }
        self.metrics = {
            "Latency": "0ms",
            "Confidence": "0.00",
            "Drift": "[green]NOMINAL[/green]"
        }
        self.logs = ["System initializing..."]
        
        # Initialize Redis connection for telemetry
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            self.redis_client.ping()
            self.update_status("Redis Broker", "[bold green]Online[/bold green]")
        except Exception:
            self.redis_client = None

        self.setup_layout()

    def setup_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=5)
        )
        
    def update_status(self, service: str, status: str):
        if service in self.statuses:
            self.statuses[service] = status

    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 3:
            self.logs.pop(0)

    def generate_body(self) -> Panel:
        # Microservice Status Table
        status_table = Table(box=None, expand=True)
        status_table.add_column("Microservice", style="cyan", no_wrap=True)
        status_table.add_column("Status", justify="right")
        
        for service, status in self.statuses.items():
            status_table.add_row(service, status)
            
        # Telemetry Metrics Table
        metrics_table = Table(box=None, expand=True)
        metrics_table.add_column("Metric", style="yellow")
        metrics_table.add_column("Value", justify="right")
        
        metrics_table.add_row("Inference Latency", self.metrics["Latency"])
        metrics_table.add_row("AI Confidence", self.metrics["Confidence"])
        metrics_table.add_row("Drift Status", self.metrics["Drift"])

        # Grid to hold both tables
        main_grid = Table.grid(expand=True)
        main_grid.add_column(ratio=1)
        main_grid.add_column(ratio=1)
        main_grid.add_row(
            Panel(status_table, title="[bold white]Service Core[/bold white]", border_style="bright_black", box=box.ROUNDED),
            Panel(metrics_table, title="[bold white]Live Telemetry[/bold white]", border_style="bright_black", box=box.ROUNDED)
        )

        return Panel(
            Align.center(main_grid),
            title="[bold white]SYSTEM MONITOR[/bold white]",
            border_style="bright_black",
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def fetch_telemetry(self):
        """Fetches the latest telemetry message from Redis."""
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
                self.redis_client.ping()
                self.update_status("Redis Broker", "[bold green]Online[/bold green]")
            except:
                return

        try:
            # Use XREVRANGE to get the most recent message from telemetry_stream
            messages = self.redis_client.xrevrange("telemetry_stream", count=1)
            if messages:
                _, payload = messages[0]
                data = json.loads(payload["data"])
                
                latency = data.get("latency_ms", 0)
                conf = data.get("avg_confidence", 0.0)
                drift = data.get("drift_detected", False)
                status = data.get("status", "UNKNOWN")

                self.metrics["Latency"] = f"{latency}ms"
                self.metrics["Confidence"] = f"{conf:.2f}"
                self.metrics["Drift"] = "[bold red]DRIFT WARNING[/bold red]" if drift else "[green]NOMINAL[/green]"
                
                self.update_status("AI Processor", "[bold green]Online[/bold green]" if status != "FAIL_CLOSED" else "[bold yellow]FAIL_CLOSED[/bold yellow]")
                self.update_status("Ingress Gateway", "[bold green]Online[/bold green]")
        except Exception as e:
            self.add_log(f"Telemetry sync error: {str(e)}")

    def render(self) -> Layout:
        # Header
        self.layout["header"].update(
            Panel(
                Align.center("[bold cyan]MATRICE EDGE ANONYMIZER[/bold cyan]"),
                box=box.ROUNDED,
                style="white"
            )
        )
        
        # Body
        self.layout["body"].update(self.generate_body())
        
        # Footer
        log_content = "\n".join(self.logs)
        self.layout["footer"].update(
            Panel(
                log_content,
                title="[bold white]System Logs[/bold white]",
                border_style="bright_black",
                box=box.ROUNDED
            )
        )
        
        return self.layout

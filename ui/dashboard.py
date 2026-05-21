from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from rich.align import Align
from datetime import datetime

class DashboardManager:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.statuses = {
            "Ingress Gateway": "[grey]Pending[/grey]",
            "AI Processor": "[grey]Pending[/grey]",
            "Redis Broker": "[grey]Pending[/grey]"
        }
        self.logs = ["System initializing..."]
        
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
        table = Table(box=None, expand=True)
        table.add_column("Microservice", style="cyan", no_wrap=True)
        table.add_column("Status", justify="right")
        
        for service, status in self.statuses.items():
            table.add_row(service, status)
            
        return Panel(
            table,
            title="[bold white]Service Core[/bold white]",
            border_style="bright_black",
            box=box.ROUNDED,
            padding=(1, 2)
        )

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

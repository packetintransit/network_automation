import os
import time
import itertools
from subprocess import Popen, DEVNULL
import ipaddress
import concurrent.futures
from rich.console import Console
from rich.table import Table
from rich.pretty import pprint


console = Console()

def ping(ip):
    with Popen(['ping', '-c', '4', '-i', '0.2', str(ip)], stdout=DEVNULL) as proc:
        proc.wait()
        if proc.returncode == 0:
            return (ip, True)
        elif proc.returncode == 1:
            return (ip, False)
        else:
            return (ip, None)

def main():
    console.print("[green]Welcome to Ping Reporter![/green]")
    console.print("[cyan]Please enter the network you wish to test...[/cyan]")
    console.print("Example: < 10.20.10.0/24 >")
    while True:
        try:
            subnet = ipaddress.ip_network(input("\nEnter network: "))
            break
        except ValueError:
            console.print("[red]Invalid network. Please try again.[/red]")
    console.print("\n")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(ping, ip) for ip in subnet.hosts()]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    active_list = [ip for ip, status in results if status]
    inactive_list = [ip for ip, status in results if status is False]
    unknown_list = [ip for ip, status in results if status is None]

    table = Table(title="PING REPORT")
    table.add_column("Active Hosts", justify="center", style="green")
    table.add_column("Inactive Hosts", justify="center", style="red")
    table.add_column("Unknown Hosts", justify="center", style="magenta")
    for (a, i, u) in itertools.zip_longest(active_list, inactive_list, unknown_list):
        table.add_row(a, i, u)
    console.print(table)

if __name__ == '__main__':
    main()

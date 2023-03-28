from nornir import InitNornir
from nornir_napalm.plugins.tasks.napalm_get import napalm_get
from rich.console import Console
from rich.table import Table
import getpass

nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
password = getpass.getpass()
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
nr.inventory.defaults.data = hotel_code

console = Console()

table = Table(title="Switch Status")

table.add_column("Switch")
table.add_column("Uptime")
table.add_column("CPU")
table.add_column("Memory")

def get_switch_data(switch):
    result = nr.run(task=napalm_get, getters=["facts", "environment"], hosts=[switch])
    facts = result[switch][0].result.get("facts")
    environment = result[switch][0].result.get("environment")
    return facts, environment

switch_data = {}
for switch in nr.inventory.hosts:
    try:
        facts, environment = get_switch_data(switch)
        if not facts or not environment:
            raise ValueError(f"Failed to get data for {switch}")
        switch_data[switch] = {**facts, **environment}
    except Exception as e:
        print(f"Failed to get data for {switch}: {e}")

for switch, data in switch_data.items():
    hostname = data["hostname"]
    uptime = data["uptime_string"]
    cpu = str(data["processor_load_percent"]) + "%"
    memory = str(round(data["memory"]["used_ram"] / data["memory"]["available_ram"] * 100, 2)) + "%"
    table.add_row(hostname, uptime, cpu, memory)

console.print(table)

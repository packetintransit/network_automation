from nornir import InitNornir
from nornir_scrapli.tasks import send_command
import getpass

nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
password = getpass.getpass()
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
nr.inventory.defaults.data = hotel_code

def get_mac_address(task):
    command = "show mac address-table interface " + task.host["interface"]
    result = task.run(task=send_command, command_string=command)
    output = result.result.split("\n")
    for line in output:
        if task.host["port"] in line:
            mac_address = line.split()[1]
            task.host.data["mac_address"] = mac_address

result = nr.run(task=get_mac_address)
for host, output in result.items():
    if "data" in output.host and "mac_address" in output.host["data"]:
        print(f"{host}: {output.host['data']['mac_address']}")
    else:
        print(f"{host}: MAC address not found")


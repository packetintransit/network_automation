import json
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import getpass


def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr


def check_hardening(task):
    # Define the commands to check hardening state
    commands = [
        "show interfaces status",
        "show run | include access-list",
        "show run | include aaa",
        "show run | include snmp-server",
        "show run | include logging",
    ]

    hardening_results = {}

    for command in commands:
        result = task.run(task=netmiko_send_command, command_string=command)
        hardening_results[command] = result.result

    task.host["hardening_results"] = json.dumps(hardening_results, indent=4)


def main():
    nr = initialize_nornir()
    result = nr.run(task=check_hardening)
    print_result(result, vars=["hardening_results"])


if __name__ == "__main__":
    main()

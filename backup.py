import os
from datetime import date
import getpass
import pathlib
from nornir import InitNornir
from nornir_netmiko.tasks.netmiko_send_command import netmiko_send_command 
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file

nr = InitNornir(config_file="config.yaml")

username = input("Please enter domain username: ")
password = getpass.getpass()

hotel_code = input("Please enter hotel code: ")

nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
nr.inventory.defaults.data = {"hotel_code": hotel_code}

def backup_configurations(task):
    commands = ["show run", "show cdp neighbor detail", "show version"]
    config_dir = "config-archive"
    date_dir = os.path.join(config_dir, str(date.today()))
    hotel_dir = os.path.join(date_dir, str(task.host["hotel_code"]))
    pathlib.Path(hotel_dir).mkdir(parents=True, exist_ok=True)
    
    for command in commands:
        command_dir = os.path.join(hotel_dir, command)
        pathlib.Path(command_dir).mkdir(parents=True, exist_ok=True)
        result = task.run(task=netmiko_send_command, command_string=command)
        filename = os.path.join(command_dir, f"{task.host.name}.txt")
        task.run(task=write_file, content=result.result, filename=filename)

def main():
    targets = nr.filter(hotel_code=nr.inventory.defaults.data["hotel_code"])
    result = targets.run(name="Creating Backup Archive", task=backup_configurations)
    print_result(result)

if __name__ == '__main__':
    main()

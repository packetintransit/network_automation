from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
import getpass

def get_err_disabled_ports(task):
    command = "show interfaces status err-disabled"
    result = task.run(netmiko_send_command, command_string=command)
    return f"Err-disabled ports on {task.host.name}:\n{result.result}\n"

def main():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}

    targets = nr.filter(hotel_code=hotel_code)
    result = targets.run(task=get_err_disabled_ports)

    output_filename = "err_disabled_ports_summary.txt"
    with open(output_filename, 'w') as output_file:
        for host in result:
            output_file.write(result[host].result)
        print(f"Saved err-disabled ports information for all switches to {output_filename}")

if __name__ == "__main__":
    main()

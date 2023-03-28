from getpass import getpass
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result


def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr


def get_port_flaps(task):
    # Send command to retrieve interface information
    interfaces = task.run(
        netmiko_send_command, command_string="show interfaces", use_textfsm=True
    )

    # Extract interface data and find port flaps
    port_flaps = []
    for interface in interfaces.result:
        if "last_flapped" in interface and "flapped" in interface["last_flapped"]:
            port_flaps.append((interface["interface"], interface["last_flapped"]))

    # Prepare the output
    output = []
    if port_flaps:
        output.append(f"{task.host}: Port Flaps")
        for port, flapped in port_flaps:
            output.append(f"{port}: {flapped}")
    else:
        output.append(f"{task.host}: No Port Flaps Found")
    
    return "\n".join(output)

def save_to_file(output):
    with open("output.txt", "a") as file:
        file.write(output)
        file.write("\n")


def main():
    nr = initialize_nornir()
    result = nr.run(task=get_port_flaps)

    for host in result:
        output = result[host].result
        print(output)
        save_to_file(output)


if __name__ == "__main__":
    main()

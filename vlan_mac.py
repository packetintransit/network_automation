import getpass
import pandas as pd
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command


def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr


# Function to get MAC addresses and their connected ports
def get_mac_addresses_ports(task):
    command = "show mac address-table dynamic vlan 2"
    output = task.run(task=netmiko_send_command, command_string=command)
    lines = output.result.splitlines()

    # Parse the output lines to extract the required data
    mac_data = []
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if len(parts) >= 4:  # Check if the line contains the required information
            vlan = parts[0]
            mac = parts[1]
            _type = parts[2]
            port = parts[3]
            mac_data.append((vlan, mac, _type, port))

    return task.host.name, mac_data


def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_mac_addresses_ports)

    # Create a list of switch names and their MAC data
    switch_data = [result.result for result in results.values()]

    # Initialize the Excel writer
    with pd.ExcelWriter("mac_addresses_ports.xlsx") as writer:
        # Save the MAC data for each switch to separate sheets
        for name, mac_data in switch_data:
            sheet_name = f"{name} MACs"
            sheet_name = sheet_name[:31]  # Truncate sheet name to 31 characters
            mac_data_df = pd.DataFrame(mac_data, columns=["VLAN", "MAC Address", "Type", "Port"])
            mac_data_df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    main()

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


# Function to get interface descriptions
def get_interface_descriptions(task):
    command = "show interface description"
    output = task.run(task=netmiko_send_command, command_string=command)
    lines = output.result.splitlines()

    # Parse the output lines to extract the required data
    interface_data = []
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if len(parts) >= 4:  # Check if the line contains the required information
            interface = parts[0]
            status = parts[1]
            protocol = parts[2]
            description = " ".join(parts[3:])
            interface_data.append((interface, status, protocol, description))

    return task.host.name, interface_data


def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_interface_descriptions)

    # Create a list of switch names and their interface data
    switch_data = [result.result for result in results.values()]

    # Initialize the Excel writer
    with pd.ExcelWriter("interface_descriptions.xlsx") as writer:
        # Save the interface data for each switch to separate sheets
        for name, interface_data in switch_data:
            sheet_name = f"{name} Interfaces"
            sheet_name = sheet_name[:31]  # Truncate sheet name to 31 characters
            interface_data_df = pd.DataFrame(interface_data, columns=["Interface", "Status", "Protocol", "Description"])
            interface_data_df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    main()

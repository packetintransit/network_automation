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


# Function to get the serial number
def get_serial_number(task):
    command = "show version | include Processor board ID"
    output = task.run(task=netmiko_send_command, command_string=command)
    serial_number = output.result.split()[-1]
    task.host["serial_number"] = serial_number
    return task.host.name, serial_number


def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_serial_number)

    # Create a list of switch names and serial numbers
    switch_data = [result.result for result in results.values()]

    # Create a DataFrame and save it to an Excel file
    df = pd.DataFrame(switch_data, columns=["Switch Name", "Serial Number"])
    df.to_excel("switch_serial_numbers.xlsx", index=False)


if __name__ == "__main__":
    main()

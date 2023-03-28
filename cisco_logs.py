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


# Function to get the informational logs
def get_switch_data(task):
    # Get informational logs
    command = "show logging | include %INFO"  # Replace with the appropriate command for informational logs
    output = task.run(task=netmiko_send_command, command_string=command)
    informational_logs = output.result.splitlines()

    return task.host.name, informational_logs


def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_switch_data)

    # Create a list of switch names and informational logs
    switch_data = [result.result for result in results.values()]

    # Initialize the Excel writer
    with pd.ExcelWriter("switch_data.xlsx") as writer:
        # Save informational logs for each switch to separate sheets
        for name, informational_logs in switch_data:
            informational_logs_df = pd.DataFrame(informational_logs, columns=["Informational Logs"])
            informational_logs_df.to_excel(writer, sheet_name=f"{name} Logs", index=False)


if __name__ == "__main__":
    main()

import wmi
import os
import csv

# Define the Active Directory domain name
domain = "myfairmont.com/CPH/BSH"

# Define the path to a file to save the results
output_file = "installed_updates.csv"

# Connect to the WMI service on the local machine
wmi_service = wmi.WMI()

# Connect to the Active Directory domain controller
ads = wmi_service.Win32_ComputerSystem(Name=domain)[0].Roles("PrimaryDC")

if not ads:
    print(f"No domain controller found for domain '{domain}'.")
    exit()

dc = ads[0].Name
print(f"Found domain controller: {dc}")

# Connect to the WMI service on the domain controller
dc_service = wmi.WMI(dc)

# Query the Win32_OperatingSystem class to get a list of all computers in the domain
computers = dc_service.Win32_ComputerSystem()

# Create a list to store the installed updates on each computer
updates_list = []

# Iterate through the list of computers and check the installed updates
for computer in computers:
    print(f"Checking updates on {computer.Name}...")
    try:
        # Connect to the WMI service on the remote computer
        remote_service = wmi.WMI(computer.Name)

        # Query the Win32_QuickFixEngineering class to get the installed updates
        updates = remote_service.Win32_QuickFixEngineering()

        # Add the installed updates to the list
        updates_list.append({"Computer": computer.Name, "Updates": [update.HotFixID for update in updates]})
    except Exception as e:
        print(f"Error checking updates on {computer.Name}: {e}")

# Write the results to a CSV file
with open(output_file, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Computer", "Updates"])
    for row in updates_list:
        writer.writerow([row["Computer"], ", ".join(row["Updates"])])
        
print(f"Results written to {os.path.abspath(output_file)}.")

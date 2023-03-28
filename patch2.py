import pyad.adquery
import wmi

# Active Directory query to get all computer objects
q = pyad.adquery.ADQuery()
q.execute_query(
    attributes=["cn", "operatingSystem", "operatingSystemVersion", "dNSHostName"],
    where_clause="objectClass='computer'"
)

# List to store results
results = []

# WMI query to get installed updates on each computer
for row in q.get_results():
    # Connect to the remote machine using WMI
    hostname = row["dNSHostName"]
    try:
        c = wmi.WMI(hostname)
    except Exception as e:
        print(f"Failed to connect to {hostname}: {e}")
        continue
    
    # Query for installed updates
    installed_updates = c.Win32_QuickFixEngineering()
    
    # Append the results to the list
    results.append({
        "Computer": row["cn"],
        "Operating System": row["operatingSystem"],
        "Operating System Version": row["operatingSystemVersion"],
        "Updates": [update.Caption for update in installed_updates]
    })

# Print the results
for result in results:
    print(f"Computer: {result['Computer']}")
    print(f"Operating System: {result['Operating System']} ({result['Operating System Version']})")
    print("Updates:")
    for update in result["Updates"]:
        print(f"  - {update}")
    print("=" * 80)

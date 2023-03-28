from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
import getpass

def get_port_and_cpu_utilization(task):
    port_utilization_cmd = "show interface summary"
    cpu_utilization_cmd = "show processes cpu sorted"
    
    port_utilization = task.run(netmiko_send_command, command_string=port_utilization_cmd)
    cpu_utilization = task.run(netmiko_send_command, command_string=cpu_utilization_cmd)

    return f"Port utilization on {task.host.name}:\n{port_utilization.result}\nCPU utilization on {task.host.name}:\n{cpu_utilization.result}\n"

def main():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}

    targets = nr.filter(hotel_code=hotel_code)
    result = targets.run(task=get_port_and_cpu_utilization)

    output_filename = "port_and_cpu_utilization_summary.txt"
    with open(output_filename, 'w') as output_file:
        for host in result:
            output_file.write(result[host].result)
        print(f"Saved port and CPU utilization information for all switches to {output_filename}")

if __name__ == "__main__":
    main()

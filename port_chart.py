import getpass
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F

def get_nornir_credentials():
    username = input("Please enter domain username: ")
    password = getpass.getpass()
    hotel_code = input("Please enter hotel code: ")
    return (username, password, hotel_code)

def initialize_nornir(username, password):
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.defaults.username = username
    nr.inventory.defaults.password = password
    return nr

def get_active_ports(task):
    interfaces = task.run(
        task=netmiko_send_command, command_string="show interfaces", use_textfsm=True
    )
    active_ports = sum(1 for interface in interfaces.result if interface["link_status"] == "up")
    return active_ports

def plot_active_ports_chart(hostnames, active_ports):
    root = tk.Tk()
    root.title("Active Ports in Cisco Switches")

    # set window size to match screen resolution
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Sort the hostnames and active_ports lists in descending order of active ports
    sorted_data = sorted(zip(hostnames, active_ports), key=lambda x: x[1], reverse=True)
    hostnames, active_ports = zip(*sorted_data)

    ax.bar(hostnames, active_ports)
    ax.set_xlabel("Switches")
    ax.set_ylabel("Number of Active Ports")
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylim(0, max(active_ports))
    ax.set_yticks(range(max(active_ports) + 1))

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    tk.mainloop()

def main():
    username, password, hotel_code = get_nornir_credentials()
    nr = initialize_nornir(username, password)
    devices = nr.filter(F(hotel_code=hotel_code))

    hostnames = []
    active_ports = []

    for device in devices.inventory.hosts.values():
        hostnames.append(device.name)
        active_ports.append(nr.run(task=get_active_ports, name=device.name)[device.name].result)

    plot_active_ports_chart(hostnames, active_ports)

if __name__ == "__main__":
    main()

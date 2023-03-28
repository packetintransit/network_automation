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

def get_cpu_usage(task):
    cpu_output = task.run(
        netmiko_send_command, command_string="show processes cpu sorted"
    )
    cpu_usage = parse_cpu_usage(cpu_output.result)
    task.host["cpu_usage"] = cpu_usage

def parse_cpu_usage(output):
    lines = output.splitlines()
    for line in lines:
        if "CPU utilization for five seconds" in line:
            cpu_usage = line.split(":")[-1].strip().split("%")[0]
            return float(cpu_usage)
    return 0

def plot_cpu_usage_chart(hostnames, cpu_usages):
    root = tk.Tk()
    root.title("CPU Usage of Cisco Switches")

    # set window size to match screen resolution
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Sort the hostnames and cpu_usages lists in descending order of CPU usage
    sorted_data = sorted(zip(hostnames, cpu_usages), key=lambda x: x[1], reverse=True)
    hostnames, cpu_usages = zip(*sorted_data)

    ax.bar(hostnames, cpu_usages)
    ax.set_xlabel("Switches")
    ax.set_ylabel("CPU Usage (%)")
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    tk.mainloop()

def main():
    username, password, hotel_code = get_nornir_credentials()
    nr = initialize_nornir(username, password)
    nr_with_hotel_code = nr.filter(F(hotel_code=hotel_code))
    result = nr_with_hotel_code.run(task=get_cpu_usage)

    hostnames = [host.name for host in nr_with_hotel_code.inventory.hosts.values()]
    cpu_usages = [host["cpu_usage"] for host in nr_with_hotel_code.inventory.hosts.values()]

    plot_cpu_usage_chart(hostnames, cpu_usages)

if __name__ == "__main__":
    main()

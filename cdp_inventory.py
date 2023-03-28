from nornir import InitNornir
from nornir_utils.plugins.functions import print_result, print_title
from nornir_netmiko.tasks.netmiko_send_command import netmiko_send_command, netmiko_send_config
import getpass


nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
nr.inventory.defaults.username = username
password = getpass.getpass()
nr.inventory.defaults.password = password
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.data = hotel_code


def cdp_map(task):
    r = task.run(task=netmiko_send_command, command_string="show cdp neighbor", use_genie=True)
    task.host["facts"] = r.result
    outer = task.host["facts"]
    indexer = outer['cdp']['index']
    for idx in indexer:
        local_intf = indexer[idx]['local_interface']
        remote_port = indexer[idx]['port_id']
        remote_id = indexer[idx]['device_id']
        cdp_config = task.run(netmiko_send_config, name="Automating CDP Network Descriptions", config_commands=[
            "interface " + str(local_intf),
            "description Connected to " + str(remote_id) + " via its " + str(remote_port) + " interface"]
                              )


results = nr.run(task=cdp_map)
print_result(results)

from nornir import InitNornir
from nornir_scrapli.tasks import send_command, send_config
from nornir_utils.plugins.functions import print_result, print_title
import getpass


nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
nr.inventory.defaults.username = username
password = getpass.getpass()
nr.inventory.defaults.password = password
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.data = hotel_code


def cdp_map(task):
    r = task.run(task=send_command, command_string="show cdp neighbor", severity_level=logging.DEBUG)
    task.host["facts"] = r.result.genie_parse_output()
    outer = task.host["facts"]
    indexer = outer['cdp']['index']
    for idx in indexer:
        local_intf = indexer[idx]['local_interface']
        remote_port = indexer[idx]['port_id']
        remote_id = indexer[idx]['device_id']
        cdp_config = task.run(send_config, name="Automating CDP Network Descriptions", 
                              config=f"interface {local_intf}\n"
                                     f"description Connected to {remote_id} via its {remote_port} interface\n"
                              )


results = nr.run(task=cdp_map)
print_result(results)

import getpass
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr

def get_last_user(task):
    r = task.run(netmiko_send_command, command_string="show archive log config all")
    last_user = r.result.splitlines()[-1].split()[-1]
    task.host["last_user"] = last_user

def main():
    nr = initialize_nornir()
    targets = nr.filter(hotel_code=nr.inventory.defaults.data["hotel_code"])
    result = targets.run(task=get_last_user)
    print_result(result, vars=["last_user"])

if __name__ == "__main__":
    main()

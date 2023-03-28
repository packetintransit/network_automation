from nornir import InitNornir
from nornir_netmiko.tasks.netmiko_send_command import netmiko_send_command 
from nornir_utils.plugins.functions import print_result
import csv
import getpass

nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
nr.inventory.defaults.username = username
password = getpass.getpass()
nr.inventory.defaults.password = password
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.data = hotel_code


def dev_info(task):
    r = task.run(netmiko_send_command, command_string="show version", use_genie=True)
    task.host["facts"] = r.result
    serial = task.host['facts']['version']['chassis_sn']
    hoster = task.host['facts']['version']['hostname']
    interno = task.host['facts']['version']['number_of_intfs']
    image = task.host['facts']['version']['system_image']
    im_type = task.host['facts']['version']['image_type']
    operating = task.host['facts']['version']['os']
    up = task.host['facts']['version']['uptime']
    ver = task.host['facts']['version']['version']
    created = task.host['facts']['version']['compiled_date']

    with open('inventory.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        csvdata = ('BSH', task.host.hostname, hoster, serial,
                   interno, image, im_type, operating, up, ver, created)
        writer.writerow(csvdata)


def main() -> None:
    result = nr.run(task=dev_info)
    print_result(result)


if __name__ == '__main__':
    main()
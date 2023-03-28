from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from pysnmp.hlapi import *
import getpass

# Initialize Nornir
def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr

# SNMP v3 function
def snmp_v3_query(host, user, auth_key, priv_key, oid):
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               UsmUserData(user, authKey=auth_key, privKey=priv_key,
                           authProtocol=usmHMACSHAAuthProtocol,
                           privProtocol=usmAesCfb128Protocol),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        return str(error_indication)
    elif error_status:
        return f'{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or "?"}'
    else:
        return ', '.join([f'{x.prettyPrint()} = {y.prettyPrint()}' for x, y in var_binds])

# SNMP task
def fetch_snmp_data(task):
    snmp_user = "Accor-Switch-SNMP-User"
    auth_key = "#RsZ5+ktY%tw9]o*t7%T!VD%JnT"
    priv_key = "$96D5&+ktY%tw9]o(t7%T!JD%Jn"
    oid = "1.3.6.1.2.1.1.1.0"  # System Description

    snmp_result = snmp_v3_query(task.host.hostname, snmp_user, auth_key, priv_key, oid)
    task.host["snmp_data"] = snmp_result

# Main function
def main():
    nr = initialize_nornir()
    result = nr.run(task=fetch_snmp_data)
    print_result(result, vars=["snmp_data"])

if __name__ == "__main__":
    main()

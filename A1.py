from logging import FileHandler, Formatter, getLogger, INFO
from netmiko import ConnectHandler
import difflib
import logging

# Establish router information
router_info = {
    'device_type': 'cisco_ios',
    'host': '192.168.56.101',
    'username': 'prne',
    'password': 'cisco123!',
    'secret': 'class123!',
}

# IPsec parameters
isakmp_policy = 10  # Lower number means higher priority
crypto_map = 'VPN_MAP'  # Defines IPsec policies for encryption
shared_key = 'Th3cra!c$f@rfr0mm!ghty'  # Pre-shared key for VPN connection

# Configure logging
def configure_logging():
    logger = getLogger()
    logger.setLevel(INFO)
    file_handler = FileHandler('syslog_events_monitoring.txt')
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# SSH connection
def ssh(router_info):
    try:
        with ConnectHandler(**router_info) as ssh_connection:
            ssh_connection.enable()
            print("SSH connection successful")
            ssh_connection.send_command("! SSH Connection established.")
    except Exception as e:
        print(f"Error establishing SSH connection: {str(e)}")

# Telnet connection
def telnet(router_info):
    try:
        with ConnectHandler(**router_info) as telnet_connection:
            telnet_connection.send_command("! Telnet connection established.")
    except Exception as e:
        print(f"Error establishing Telnet connection: {str(e)}")

# Change hostname
def hostname_change(router_info):
    new_hostname = input("Enter new hostname: ")
    try:
        with ConnectHandler(**router_info) as ssh_connection:
            ssh_connection.enable()
            commands = [f"hostname {new_hostname}"]
            output = ssh_connection.send_config_set(commands)
            print("Hostname changed successfully:")
            print(output)
    except Exception as e:
        print(f"Error changing hostname: {str(e)}")

# Retrieve running configuration
def grab_router_config(router_info):
    try:
        with ConnectHandler(**router_info) as ssh_connection:
            ssh_connection.enable()
            output = ssh_connection.send_command("show running-config")
            return output
    except Exception as e:
        print(f"Error retrieving running configuration: {str(e)}")
        return ""

# Compare configurations
def config_hardening_compare(device_config, hardening_advice):
    d = difflib.Differ()
    diff = list(d.compare(device_config.splitlines(), hardening_advice.splitlines()))
    print("\nConfiguration Differences:")
    print("\n".join(diff))

# ACL configuration
def acl_list(router_info, acl_file):
    try:
        with ConnectHandler(**router_info) as ssh_connection:
            ssh_connection.enable()
            with open(acl_file, 'r') as file:
                acl_config = file.read().splitlines()
            output = ssh_connection.send_config_set(acl_config)
            print("ACL configuration applied:")
            print(output)
    except FileNotFoundError:
        print(f"Error: ACL file {acl_file} not found.")
    except Exception as e:
        print(f"Error applying ACL configuration: {str(e)}")

# IPsec configuration
def ipsec_config(router_info, isakmp_policy, crypto_map, shared_key):
    try:
        with ConnectHandler(**router_info) as ssh_connection:
            ssh_connection.enable()

            isakmp_config = [
                f"crypto isakmp policy {isakmp_policy}",
                "encryption aes-256",
                "hash sha256",
                "authentication pre-share",
                "group 14",
                "lifetime 28800",
            ]

            shared_key_config = [
                f"crypto isakmp key {shared_key} address 0.0.0.0",
            ]

            crypto_map_config = [
                f"crypto map {crypto_map} 10 ipsec-isakmp",
                "set peer 0.0.0.0",
                "set transform-set myset",
                "match address 100",
            ]

            output = ssh_connection.send_config_set(isakmp_config + shared_key_config + crypto_map_config)
            print("IPsec configuration applied successfully:")
            print(output)
    except Exception as e:
        print(f"Error configuring IPsec: {str(e)}")

# Main menu
def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Change Hostname")
        print("2. Establish SSH Connection")
        print("3. Establish Telnet Connection")
        print("4. Retrieve Running Configuration")
        print("5. Compare Configurations")
        print("6. Configure Event Logging")
        print("7. Apply ACL Configuration")
        print("8. Configure IPsec")
        print("0. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            hostname_change(router_info)
        elif choice == '2':
            ssh(router_info)
        elif choice == '3':
            telnet(router_info)
        elif choice == '4':
            config = grab_router_config(router_info)
            print("Running Configuration:\n", config)
        elif choice == '5':
            hardening_advice = """! Example hardening advice here"""
            device_config = grab_router_config(router_info)
            config_hardening_compare(device_config, hardening_advice)
        elif choice == '6':
            configure_logging()
        elif choice == '7':
            acl_file = input("Enter the path to the ACL file: ")
            acl_list(router_info, acl_file)
        elif choice == '8':
            ipsec_config(router_info, isakmp_policy, crypto_map, shared_key)
        elif choice == '0':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()

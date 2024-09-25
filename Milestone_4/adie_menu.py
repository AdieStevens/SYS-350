import json
import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim 

# Load vCenter configuration from JSON file 
def load_vcenter_config(config_file="vcenter-conf.json"):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config['vcenter'][0]

# Function to connect to vCenter

def connect_to_vcenter(vcenter_host, username, password):
    context = ssl._create_unverified_context()
    si = SmartConnect(host=vcenter_host, user=username, pwd=password, sslContext=context)
    atexit.register(Disconnect, si)
    return si

# Requirement 1: Get vcenter basic information
def get_vcenter_info(si):
    about_info = si.content.about
    return about_info

# Requirement 2: Get current session info
def get_session_info(si):
    session_manager = si.content.sessionManager
    session_info = session_manager.currentSession
    return {
        'User': session_info.userName,
        'vCenter Server': si._stub.host,
        'Source IP': session_info.ipAddress
    }

# Requirement 3: Search and filter VMs
def search_vms(si, vm_name_filter=None):
    container = si.content.viewManager.CreateContainerView(
        si.content.rootFolder, [vim.VirtualMachine], True)
    vms = container.view
    container.Destroy()

    vm_info_list = []
    for vm in vms:
        if vm_name_filter and vm_name_filter not in vm.name:
            continue
        
        vm_info = {
            'VM Name': vm.name,
            'Power State': vm.runtime.powerState,
            'CPUs': vm.config.hardware.numCPU,
            'Memory': vm.config.hardware.memoryMB / 1024,
            'IP Address': vm.guest.ipAddress
        }
        vm_info_list.append(vm_info)

    return vm_info_list

# Main Menu

def menu():
    #Load config and get credentials
    config = load_vcenter_config()
    vcenter_host = config['vcenterhost']
    username = config['vcenteradmin']
    password = input(f"Enter password for {username}: ")

    # Connect to vCenter
    si = connect_to_vcenter(vcenter_host, username, password)

    while True:
        print("\nMenu:")
        print("1. Get vCenter Info")
        print("2. Get Session Info")
        print("3. Search VMs")
        print("4. Exit")

        choice = input("Select an option (1-4):")

        if choice == '1':
            info = get_vcenter_info(si)
            print(f"vCenter Info:{si.content.about}")

        elif choice == '2':
            session_info = get_session_info(si)
            print(f"Session Info:\nUser: {session_info['User']}\nvCenter Server: {session_info['vCenter Server']}\nSource IP: {session_info['Source IP']}")

        elif choice == '3':
            filter_name = input("Enter VM name filter (leave empty for all VMs): ")
            vms = search_vms(si, filter_name)
            print("VMs found:")
            for vm in vms:
                print(f"Name: {vm['VM Name']}, Power State: {vm['Power State']}, CPUs: {vm['CPUs']}, Memory: {vm['Memory (GB)']}GB, IP: {vm['IP Address']}")

        elif choice == '4':
            print("Dueces")
            break

        else:
            print("Invalid choice. Please select an option between 1 and 4")

if __name__ == "__main__":
    menu()





'''
    print("[1] Vcenter Info ")
    print("[2] Session Details")
    print("[3] VM Details")
    print("[0] Exit")

menu()
option = int(input("Enter Option Number:"))

while option != 0:
    if option == 1:
        # Option 1 function here
        print("option 1")
    elif option == 2:
        # Option 2 function here
        print ("option 2")
    elif option == 3:
        #option 3 function here
        print ("option 3")
    else:
        print("Invalid Option - Please choose from the list above")

    menu()
    option = int(input("Enter Option Number:"))

print ("Deuces")
'''

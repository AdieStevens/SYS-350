import getpass
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
def list_and_get_vm_details(si):
    container = si.content.viewManager.CreateContainerView(
        si.content.rootFolder, [vim.VirtualMachine], True)
    vms = container.view
    container.Destroy()

    # Store all VM names
    vm_names = [vm.name for vm in vms]
    print("\nList of VMs:")
    for name in vm_names:
        print(f"- {name}")

    # Prompt user to select a VM name
    selected_vm_name = input("\nEnter the VM name to get details: ").strip()
    
    # Find the specific VM
    for vm in vms:
        if vm.name == selected_vm_name:
            vm_info = {
                'VM Name': vm.name,
                'Power State': vm.runtime.powerState,
                'CPUs': vm.config.hardware.numCPU if vm.config.hardware else "N/A",
                'Memory (GB)': vm.config.hardware.memoryMB / 1024 if vm.config.hardware else "N/A",
                'IP Address': vm.guest.ipAddress if vm.guest.ipAddress else "N/A"
            }
            print("\nVM Details:")
            print(f"Name: {vm_info['VM Name']}")
            print(f"Power State: {vm_info['Power State']}")
            print(f"CPUs: {vm_info['CPUs']}")
            print(f"Memory (GB): {vm_info['Memory (GB)']}GB")
            print(f"IP Address: {vm_info['IP Address']}")
            return
    
    # If no VM was found with the given name
    print(f"\nNo VM found with the name: {selected_vm_name}")

# Function to power on a VM
def power_on_vm(si):
    vm = select_vm(si)
    if vm:
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            print(f"Powering on VM: {vm.name}")
            task = vm.PowerOnVM_Task()
        else:
            print(f"VM {vm.name} is already powered on.")

# Function to power off a VM
def power_off_vm(si):
    vm = select_vm(si)
    if vm:
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            print(f"Powering off VM: {vm.name}")
            task = vm.PowerOffVM_Task()
        else:
            print(f"VM {vm.name} is already powered off.")

# Function to take a snapshot of a VM
def take_snapshot(si):
    vm = select_vm(si)
    if vm:
        snapshot_name = input("Enter the snapshot name: ")
        snapshot_description = input("Enter snapshot description: ")
        print(f"Taking snapshot of VM: {vm.name}")
        task = vm.CreateSnapshot_Task(name=snapshot_name, description=snapshot_description, memory=False, quiesce=True)

# Function to delete a VM from disk
def delete_vm(si):
    vm = select_vm(si)
    if vm:
        confirm = input(f"Are you sure you want to delete VM {vm.name} from disk? (y/n): ")
        if confirm.lower() == 'y':
            print(f"Deleting VM: {vm.name}")
            task = vm.Destroy_Task()

# Function to restore the latest snapshot
def restore_latest_snapshot(si):
    vm = select_vm(si)
    if vm and vm.snapshot:
        latest_snapshot = vm.snapshot.rootSnapshotList[-1]
        print(f"Reverting to latest snapshot for VM: {vm.name}")
        task = latest_snapshot.snapshot.RevertToSnapshot_Task()
    else:
        print(f"No snapshots found for VM: {vm.name}")

# Function to change memory of a VM
def change_memory(si):
    vm = select_vm(si)
    if vm:
        new_memory_gb = int(input(f"Enter new memory size (in GB) for VM {vm.name}: "))
        spec = vim.vm.ConfigSpec()
        spec.memoryMB = new_memory_gb * 1024
        print(f"Updating memory of VM: {vm.name}")
        task = vm.ReconfigVM_Task(spec)

# Utility function to select a VM
def select_vm(si):
    container = si.content.viewManager.CreateContainerView(
        si.content.rootFolder, [vim.VirtualMachine], True)
    vms = container.view
    container.Destroy()

    vm_names = [vm.name for vm in vms]
    print("\nList of VMs:")
    for index, name in enumerate(vm_names):
        print(f"{index + 1}. {name}")

    vm_choice = int(input("\nSelect a VM by number: ")) - 1
    if vm_choice >= 0 and vm_choice < len(vms):
        return vms[vm_choice]
    else:
        print("Invalid choice.")
        return None

# Main Menu
def menu():
    # Load config and get credentials
    config = load_vcenter_config()
    vcenter_host = config['vcenterhost']
    username = config['vcenteradmin']
    password = getpass.getpass(f"Enter password for {username}: ")

    # Connect to vCenter
    si = connect_to_vcenter(vcenter_host, username, password)

    while True:
        print("\nMenu:")
        print("1. Get vCenter Info")
        print("2. Get Session Info")
        print("3. Search VMs")
        print("4. VM Actions")
        print("5. Exit")

        choice = input("Select an option (1-5): ")

        if choice == '1':
            info = get_vcenter_info(si)
            print(f"vCenter Info: {info}")

        elif choice == '2':
            session_info = get_session_info(si)
            print(f"Session Info:\nUser: {session_info['User']}\nvCenter Server: {session_info['vCenter Server']}\nSource IP: {session_info['Source IP']}")

        elif choice == '3':
            list_and_get_vm_details(si)

        elif choice == '4':
            while True:
                print("\nVM Actions:")
                print("1. Power On a VM")
                print("2. Power Off a VM")
                print("3. Take a Snapshot")
                print("4. Delete a VM from Disk")
                print("5. Restore Latest Snapshot")
                print("6. Change Memory of VM")
                print("7. Go Back")

                action_choice = input("Select an action (1-7): ")

                if action_choice == '1':
                    power_on_vm(si)
                elif action_choice == '2':
                    power_off_vm(si)
                elif action_choice == '3':
                    take_snapshot(si)
                elif action_choice == '4':
                    delete_vm(si)
                elif action_choice == '5':
                    restore_latest_snapshot(si)
                elif action_choice == '6':
                    change_memory(si)
                elif action_choice == '7':
                    break
                else:
                    print("Invalid choice. Please select an option between 1 and 7")

        elif choice == '5':
            print("Dueces")
            break

        else:
            print("Invalid choice. Please select an option between 1 and 5")

if __name__ == "__main__":
    menu()

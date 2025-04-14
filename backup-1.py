from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime

def create_client(subscription_id):
    credential = AzureCliCredential()
    return ComputeManagementClient(credential, subscription_id)
def fetch_vms(resource_group, subscription_id):
    compute_client = create_client(subscription_id)
    instances = [vm for vm in compute_client.virtual_machines.list(resource_group_name=resource_group)]
    return instances

def fetch_snapshots(resource_group, subscription_id):
    compute_client = create_client(subscription_id)
    snapshots = [snapshot for snapshot in compute_client.snapshots.list_by_resource_group(resource_group_name=resource_group)]
    return snapshots
def list_vms_by_zone(subscription_id, zone):
    compute_client = create_client(subscription_id)
    result = []

    for vm in compute_client.virtual_machines.list_all():
        if vm.location.lower() != zone.lower():
            continue

        name = vm.name
        tags = vm.tags or {}
        backup_enabled = tags.get("backup", "false").lower() == "true"

        os_disk_name = vm.storage_profile.os_disk.name

        # Get snapshot list
        latest_backup = "Never"
        snapshots = compute_client.snapshots.list()
        matching_snaps = [
            snap for snap in snapshots
            if snap.creation_data and snap.creation_data.source_resource_id and os_disk_name in snap.creation_data.source_resource_id
        ]
        if matching_snaps:
            latest = max(snap.time_created for snap in matching_snaps)
            latest_backup = latest.strftime("%Y-%m-%d %H:%M:%S")

        result.append({
            "Instance": name,
            "Backup Enabled": backup_enabled,
            "Disk": os_disk_name,
            "Last Backup": latest_backup
        })

    return result

def print_result(table_data):
    print(f"{'Instance':<25} {'Backup Enabled':<15} {'Disk':<25} {'Last Backup'}")
    for row in table_data:
        print(f"{row['Instance']:<25} {str(row['Backup Enabled']):<15} {row['Disk']:<25} {row['Last Backup']}")

if __name__ == "__main__":
    #subscription_id = input("Enter your subscription ID: ").strip()
    zone = input("Enter the zone (e.g. eastus): ").strip()
    subscription_id = "31169275-2308-4cdd-8d7a-f39ffd65bbf8"
    resource_group = "xcc-assessment-haytam"
    vms = fetch_vms(resource_group, subscription_id)
    for vm in vms:
        print(f"VM Name: {vm.name}")

    print("\nFetching Snapshots...")
    snapshots = fetch_snapshots(resource_group, subscription_id)
    for snapshot in snapshots:
        print(f"Snapshot Name: {snapshot.name}")


    vm_table = list_vms_by_zone(subscription_id, zone)
    print_result(vm_table)

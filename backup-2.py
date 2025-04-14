from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime, timezone
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def create_client(subscription_id):
    credential = AzureCliCredential()
    return ComputeManagementClient(credential, subscription_id)

def get_backup_enabled_vms(compute_client):
    vms = []
    for vm in compute_client.virtual_machines.list_all():
        tags = vm.tags or {}
        if tags.get("backup", "false").lower() == "true":
            vms.append(vm)
    return vms

def last_snapshot_date(compute_client, os_disk_name):
    today = datetime.now(timezone.utc).date()
    for snapshot in compute_client.snapshots.list():
        if snapshot.creation_data.source_resource_id and os_disk_name in snapshot.creation_data.source_resource_id:
            if snapshot.time_created.date() == today:
                return snapshot.time_created
    return None

def wait_for_snapshots(compute_client, resource_group, snapshot_names):
    for name in snapshot_names:
        logging.info(f"Waiting for snapshot {name} to complete...")
        while True:
            snapshot = compute_client.snapshots.get(resource_group, name)
            if snapshot.provisioning_state == "Succeeded":
                logging.info(f"Snapshot {name} is done.")
                break
            elif snapshot.provisioning_state in ("Failed", "Canceled"):
                logging.error(f"Snapshot {name} failed with status: {snapshot.provisioning_state}")
                break
            else:
                time.sleep(3)

def create_snapshots(subscription_id, dry_run=False):
    logging.info("Starting backup process")
    compute_client = create_client(subscription_id)
    vms = get_backup_enabled_vms(compute_client)
    logging.info(f"Found {len(vms)} instances")

    snapshot_names = []

    for vm in vms:
        logging.info(f"Instance: {vm.name}")
        logging.info(f"Backup Enabled: True")

        os_disk = vm.storage_profile.os_disk
        disk_name = os_disk.name
        resource_group = vm.id.split("/")[4]

        last_snap = last_snapshot_date(compute_client, disk_name)
        if last_snap:
            logging.info(f"Last backup was {last_snap} ago")
            logging.info("Skipping backup creation since the last backup is too recent")
            continue

        snapshot_name = f"{vm.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if dry_run:
            logging.info(f"[Dry Run] Would create snapshot '{snapshot_name}' for disk '{disk_name}' in resource group '{resource_group}'")
        else:
            snapshot_config = {
                "location": vm.location,
                "creation_data": {
                    "create_option": "Copy",
                    "source_resource_id": os_disk.managed_disk.id
                }
            }
            logging.info("Starting asynchronous backup creation")
            compute_client.snapshots.begin_create_or_update(resource_group, snapshot_name, snapshot_config)
            snapshot_names.append(snapshot_name)

    if not dry_run:
        wait_for_snapshots(compute_client, resource_group, snapshot_names)
        logging.info("All snapshots done")
    else:
        logging.info("Dry run complete — no snapshots were created.")

if __name__ == "__main__":
    #subscription_id = input("Enter your subscription ID: ").strip()
    subscription_id = "31169275-2308-4cdd-8d7a-f39ffd65bbf8"
    mode = input("Run in dry mode? (yes/no): ").strip().lower()
    create_snapshots(subscription_id, dry_run=(mode == "yes"))

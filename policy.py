import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def create_client(subscription_id):
    credential = AzureCliCredential()
    return ComputeManagementClient(credential, subscription_id)

def group_snapshots_by_disk(compute_client):
    grouped = defaultdict(list)
    for snapshot in compute_client.snapshots.list():
        if snapshot.creation_data.source_resource_id:
            disk_id = snapshot.creation_data.source_resource_id.split("/")[-1]
            grouped[disk_id].append(snapshot)
    return grouped

def apply_retention_policy(subscription_id):
    logging.info("Checking backups against retention policy")
    compute_client = create_client(subscription_id)
    snapshots_by_disk = group_snapshots_by_disk(compute_client)
    now = datetime.now(timezone.utc)

    for disk_id, snapshots in snapshots_by_disk.items():
        logging.info(f"Checking backups for disk {disk_id}")
        # Sort snapshots newest to oldest
        snapshots.sort(key=lambda s: s.time_created, reverse=True)

        keepers = set()

    
        daily = {}
        weekly = {}

        for snap in snapshots:
            age_days = (now - snap.time_created).days
            snap_date = snap.time_created.date()
            if age_days <= 7:
           
                if snap_date not in daily:
                    daily[snap_date] = snap
            else:
              
                year, week, _ = snap_date.isocalendar()
                week_key = (year, week)
                if week_key not in weekly:
                    weekly[week_key] = snap

  
        keepers.update(s.id for s in daily.values())
        keepers.update(s.id for s in weekly.values())

        for snap in snapshots:
            if snap.id not in keepers:
                logging.info(f"Deleting snapshot {snap.name}")
                rg_name = snap.id.split("/")[4]
                compute_client.snapshots.begin_delete(rg_name, snap.name)

if __name__ == "__main__":
    subscription_id = "31169275-2308-4cdd-8d7a-f39ffd65bbf8"
    apply_retention_policy(subscription_id)

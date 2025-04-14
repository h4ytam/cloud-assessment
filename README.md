# Azure VM Backup Manager

## 🛡️ Overview

The **Azure VM Backup Manager** is a Python toolset for managing backups of Azure virtual machines (VMs). It supports:

- Listing VMs and their backup status
- Creating daily snapshots for primary disks of VMs tagged for backup
- Applying a retention policy to automatically delete old snapshots

Backups are managed using VM **tags** (labels). A VM is considered to have backups enabled if it has a tag `backup=true`.

---

## 🧩 Features

### ✅ BACKUP-1: VM Backup Status Report
- Lists VMs in a specific region
- Shows:
  - VM Name
  - Whether backup is enabled (via tags)
  - Name of the primary disk
  - Timestamp of last backup (snapshot)

### ✅ BACKUP-2: Create Snapshots
- Creates **daily backups** (snapshots) only if no snapshot has been created **today**
- Handles snapshot creation **asynchronously**
- Optional dry-run mode to validate before creating

### ✅ BACKUP-3: Retention Policy
- Keeps **1 snapshot per day** for the **last 7 days**
- Keeps **1 snapshot per week** for backups **older than 7 days**
- Deletes older snapshots to save storage cost

---

## 🧰 Azure Resources Used

- **Azure Virtual Machines**
- **Managed Disks** (OS & data disks)
- **Azure Snapshots**
- **Tags on Virtual Machines** (`backup=true`)
- **Azure Resource Groups**
- **Azure Identity** for authentication

---

## 🐍 Python Libraries

| Library | Purpose |
|--------|---------|
| [`azure-identity`](https://pypi.org/project/azure-identity/) | Handles authentication using `AzureCliCredential` |
| [`azure-mgmt-compute`](https://pypi.org/project/azure-mgmt-compute/) | Manages compute resources (VMs, disks, snapshots) |
| `datetime` | Date/time operations |
| `collections` | Grouping snapshots by disk |
| `logging` | Console logging and diagnostics |

---

## 📦 Installation

```bash
pip install azure-identity azure-mgmt-compute

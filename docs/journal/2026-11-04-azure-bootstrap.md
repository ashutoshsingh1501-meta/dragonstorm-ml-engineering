# Lab Journal — 2026-11-04: Personal Azure VM Bootstrap

> **Evidence standard:** This is a retrospective record of observed Azure Portal screenshots and terminal outputs shared during the guided session. Commands shown as completed were executed by the user. Do not treat screenshots or this document as a deployable IaC configuration.

## Scope and boundaries

This is an **independent greenfield learning lab**, managed from a personal laptop in a personally owned Azure environment. ML computation is intended to run on Azure—not on the personal laptop. Only public/openly licensed models, datasets, and original code should be used. No third-party private artifacts are available or needed.

## 1. Account and regional compute prerequisites

- Personal Azure account and subscription activated; owner access verified.
- Azure free-trial offer confirmed; exact balance is not essential to choose the architecture.
- `Microsoft.Compute` resource provider was registered.
- **Central India** quota observation: 4 total regional vCPUs; several general-purpose families have individual 4-vCPU quotas. Some GPU family quotas show 0; other legacy families show 6, but **regional quota, SKU availability, and capacity still constrain deployment**.
- Initial VM chooser returned `NotAvailableForSubscription` on its default SKU.
- Selecting an availability zone limited available SKUs; changing **Availability options** to `No infrastructure redundancy required` exposed more options.
- Selected `Standard_D4as_v5` (4 vCPU, 16 GiB RAM), a non-burstable general-purpose CPU VM.
- Price displayed during configuration: **USD 0.1110 per compute hour** (portal estimate; not a final all-inclusive bill; disk/networking and other charges separate).

**Why not a B-series machine for the first benchmark?** CPU credit behavior makes sustained load experiments less directly interpretable. GPU capacity and quota will be evaluated as a separate later milestone.

## 2. Azure VM deployment — completed

| Property | Configured or observed |
| --- | --- |
| Region | Central India |
| Resource group | `rg-dragonstorm-ml-lab` |
| VM name | `vm-dragonstorm-ml-01` |
| Size | `Standard_D4as_v5` |
| Image | Ubuntu Server 24.04 LTS, x64 |
| OS disk | 128 GiB Premium SSD; delete with VM enabled |
| Availability | No infrastructure redundancy required |
| Admin authentication | SSH public key generated during VM creation |
| NIC network security group | `vm-dragonstorm-ml-01-nsg` |
| Initial public inbound ports | None |
| Network access | Public IP assigned; TCP/22 later allowed only from current personal client IP |
| NIC/public IP cleanup | Delete public IP and NIC with VM enabled |
| Auto-shutdown (initial setting) | Daily at **20:00 IST**; notification configured. **Later disabled temporarily** for uninterrupted setup (see change log below). |
| Boot diagnostics | Enabled |
| Resource tagging | Project: `dragonstorm-ml-engineering` |

The wizard initially displayed stale/inconsistent NSG and boot-diagnostics summary values. Re-selecting the intended values refreshed the Review + create page; final summary showed the NSG and boot diagnostics enabled.

Deployment completed successfully in the portal. The VM Overview subsequently displayed **Running**, and the VM Agent was ready.

**Billing note:** Deallocate when not in use to stop compute charges. Persistent managed disks and other resources can still incur charges while compute is deallocated. VM auto-shutdown has been configured, not tested.

## 3. Network, identity, and Windows SSH troubleshooting

The NSG initially had default inbound deny and no custom inbound rules. The user added one inbound rule:

| Field | Value |
| --- | --- |
| Rule | `Allow-SSH-Personal-IP` |
| Source | `My IP address` (current public client IP, intentionally omitted) |
| Destination | VM / Any |
| Destination port | 22 |
| Protocol | TCP |
| Action | Allow |
| Priority | 100 |

The first SSH attempt reached the server but failed private-key file validation on the Windows client:

```text
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions for the private key are too open.
This private key will be ignored.
Permission denied (publickey).
```

Diagnosis: the downloaded private key inherited read access for an additional local group. The user inspected and repaired permissions using Windows PowerShell:

```powershell
icacls "$env:USERPROFILE\Downloads\vm-dragonstorm-ml-01_key.pem"
icacls "$env:USERPROFILE\Downloads\vm-dragonstorm-ml-01_key.pem" /inheritance:d
icacls "$env:USERPROFILE\Downloads\vm-dragonstorm-ml-01_key.pem" /remove:g "PERSONAL\CodexSandboxUsers"
icacls "$env:USERPROFILE\Downloads\vm-dragonstorm-ml-01_key.pem"
```

The file subsequently showed only the owning user, local Administrators, and SYSTEM. **This ACL correction was specific to the observed client; never run the group-removal command blindly on another machine.**

Retrying SSH succeeded. The user reached the Ubuntu shell prompt. The initial SSH host key was accepted **before independent fingerprint verification**, which remains a separate security follow-up; success of public-key authentication does not by itself verify server identity.

**Security:** The actual VM public IP, client IP, private key, and contact details are intentionally absent from this public journal.

## 4. Guest OS hardware inventory — completed

### CPU

Command: `lscpu`

- Architecture: `x86_64`
- Online logical CPUs: `0-3` = **4 vCPUs**
- Processor label reported by guest: **AMD EPYC 7763 64-Core Processor**; this does **not** mean the VM owns 64 cores.
- Hypervisor: Microsoft; virtualization capability reported.

### Memory

Command: `free -h`

- Total: approximately **15 GiB** reported by Linux
- Used: **595 MiB** at time of observation
- Available: approximately **14 GiB**
- Swap: **0 GiB**

### Disk

Command: `df -hT`

```text
Filesystem   Type   Size  Used  Avail  Use%  Mounted on
/dev/root    ext4   123G  2.2G  121G   2%    /
```

The Ubuntu root filesystem has approximately **121 GiB free** at baseline; this is not the same as RAM-backed `tmpfs` entries in the full command output.

## 5. Ubuntu package update — completed

### Step A: update package indexes

```bash
sudo apt update
```

Result: Ubuntu `noble`, `noble-updates`, `noble-backports`, and `noble-security` repositories were reachable; **16 upgradable packages** were reported.

### Step B: inspect proposed changes

```bash
apt list --upgradable
```

16 packages were listed, including `bind9-*`, `cloud-init`, `libglib2.0-*`, `libnss3`, `tmux`, `zlib1g`, `ubuntu-pro-client` and related packages.

### Step C: upgrade

```bash
sudo apt upgrade
```

The user confirmed the transaction after inspecting the proposed changes:

```text
16 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
8 standard LTS security updates
```

Result: Package unpacking and setup finished, services were restarted, and the command returned to the shell prompt. Output said the running kernel was up to date. Some individual service restarts were deferred, and the existing login session used older binaries; this is not evidence of an overall upgrade failure.

### Step D: test reboot flag

```bash
if [ -f /var/run/reboot-required ]; then echo "REBOOT REQUIRED"; else echo "NO REBOOT REQUIRED"; fi
```

Observed output:

```text
NO REBOOT REQUIRED
```

## 6. Configuration change — temporary auto-shutdown disablement (verified)

During the same setup day (2026-11-04), the user intentionally disabled VM **Auto-shutdown** to allow uninterrupted installation and tests.

**Portal screenshot evidence:** VM Operations → Auto-shutdown shows **Off**, and VM Overview → Capabilities indicates **Auto-shutdown: Not configured**. VM Overview shows the power state **Running**.

**Operational decision:** Run the remaining installation/testing session, then manually select **Stop** in Azure Portal and verify **Stopped (deallocated)** before leaving the lab. This deallocation has **not yet happened**. Persistent disk and other separately metered resources may still accrue charges after compute deallocation.

**Rollback / future safeguard:** Re-enable a suitable automatic shutdown schedule when regular experimentation resumes. Record and verify that change separately.

## 7. Current stop point — no Docker installation yet

The **next proposed command** is:

```bash
sudo apt install -y ca-certificates curl
```

**Executed and verified.** Output: `ca-certificates` version `20260816ubuntu0.24.04.1` and `curl` version `8.5.0-2ubuntu10.16` already installed; `0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded`. Next: configure Docker's official apt repository following the official Ubuntu instructions. Docker Engine, Triton, vision models, inference requests, load tests, training runs, and model evaluations **have not yet been performed** in this lab.

## Lessons for future write-ups

1. Infrastructure prerequisites and quota are independent of SKU capacity and zonal availability.
2. A VM wizard's final configuration summary should be reconciled with field selections **before** deployment.
3. SSH requires both an appropriately scoped cloud NSG rule **and** restrictive private-key filesystem ACLs.
4. Distinguish **guest-observed usable resources** from Azure's provisioned SKU specifications.
5. Security and cost are experiment dimensions: record controlled access, resource lifetimes, and deallocation practices.
6. Maintain verifiable evidence; don't extrapolate GPU results from a CPU-only VM.

# Engineering Progress Tracker

This file records **verified outcomes only**. Planned actions are explicitly marked pending. For detailed commands and evidence, follow the dated journal.

## Current milestone — 2026-11-04

**Stage:** Personal Azure infrastructure provisioned; Linux OS prepared; Docker installation **not started**.

| ID | Milestone | Status | Evidence |
| --- | --- | --- | --- |
| I-01 | Separate personal Azure subscription | Complete | Active Azure subscription with Owner role confirmed in portal |
| I-02 | Compute resource provider registration | Complete | `Microsoft.Compute` Registered |
| I-03 | Central India quota inspection | Complete | Regional quota 4 vCPUs; VM family quotas inspected |
| I-04 | VM size and region selection | Complete | D4as_v5 selected after removing zone restriction |
| I-05 | Linux VM provisioning | Complete | Azure deployment completed; VM power state Running |
| I-06 | SSH security rule | Complete | NSG TCP/22 restricted to current public client IP; default deny inbound |
| I-07 | SSH private-key ACL fix | Complete | Unwanted group read permission removed on personal Windows client |
| I-08 | First SSH login | Complete | Ubuntu shell prompt observed |
| I-09 | CPU inventory | Complete | 4 vCPUs; AMD EPYC 7763 reported by `lscpu` |
| I-10 | RAM inventory | Complete | `free -h`: ~15 GiB total, ~14 GiB available, 0 swap |
| I-11 | Disk inventory | Complete | Root ext4: 123 GiB size, 2.2 GiB used, 121 GiB available |
| I-12 | Package index refresh | Complete | `sudo apt update` succeeded |
| I-13 | Package upgrade | Complete | 16 updated; 0 removed; 8 security updates |
| I-14 | Reboot requirement check | Complete | `NO REBOOT REQUIRED` |
| I-14a | Temporary auto-shutdown change | Complete | Azure VM Auto-shutdown page shows Off; Overview shows Not configured; VM Running |
| I-14b | End-of-session manual deallocation | **Pending** | Must confirm `Stopped (deallocated)` in Azure after lab session; compute charges continue while Running |
| I-15 | Docker prerequisites | Complete | `sudo apt install -y ca-certificates curl` succeeded; both already installed; 0 new packages, 0 upgrades |
| I-15a | Docker keyring directory setup | Complete | `ls -ld /etc/apt/keyrings/`: `drwxr-xr-x root root`; permissions 0755 confirmed |
| I-15b | Docker apt signing key file | Complete | `docker.asc` downloaded (3.8 KB; root; mode `0644`); GPG fingerprint matches documented Docker CE key `9DC8...0EBFCD88` |
| I-15c | Docker official APT repository configuration | Complete | `docker.sources` inspected: stable, `noble`, `amd64`, HTTPS, `Signed-By: /etc/apt/keyrings/docker.asc` |
| I-15d | Docker repository metadata refresh | Complete | `sudo apt update` fetched Docker `noble InRelease` (48.5 KB) and `noble/stable amd64 Packages` (73.4 KB) without errors |
| I-16 | Docker Engine packages | Complete | 7 packages installed via Docker official APT repo; Docker CE/CLI 29.9.3, containerd 2.4.2, Buildx 0.38.1, Compose 5.7.0 |
| I-16a | Docker daemon and CLI communication | Complete | `sudo docker version` returned both Client and Server 29.9.3 (API 1.56), linux/amd64; containerd 2.4.2, runc 1.5.2 |
| I-16b | First Docker test container | Complete | `sudo docker run --rm hello-world` pulled official amd64 image, printed `Hello from Docker!`, exited successfully; `--rm` cleaned up container |
| I-16c | Docker disk usage baseline | Complete | `sudo docker system df`: 1 image, 36.94 kB total (25.87 kB reclaimable), 0 containers, 0 volumes, 0 build cache |
| I-16d | Docker storage filesystem free space | Complete | `df -h /var/lib/docker`: `/dev/root` 123G total, 2.5G used, **121G available** (3% used); actual Docker root not yet independently verified |
| I-16e | Docker data-root verification | Complete | `sudo docker info --format '{{.DockerRootDir}}'` returned `/var/lib/docker`; filesystem check found 121 GiB available |
| I-17 | NVIDIA Triton | **Pending** | No image download / server launch evidence |
| I-18 | Vision inference | **Pending** | No model or inference evidence |

## Open verification items

- Independently verify the SSH host key fingerprint via a trusted out-of-band channel; the first SSH host key was accepted before this verification.
- Verify active network rule and power state before each remote connection; public client IP may change.
- **Temporary cost-control exception (2026-11-04):** Auto-shutdown is Off for today's installation/testing. Manual Stop + verified `Stopped (deallocated)` is required before finishing; restoring an automatic schedule afterward is recommended.
- Reassess image backend support, actual container size, and cost prior to downloading Triton.
- Keep GPU provisioning separate; current deployment is CPU-only.

## Documentation rules

1. For **each executed command or Azure configuration step**, record the exact action (with secrets removed), observed outcome, and any errors in the journal.
2. Update the tracker only **after** the result is reported/verified; never mark an intention as complete.
3. Note decision rationale, costs, reproducibility and rollback when relevant.
4. Never publish personal contact details, subscription IDs, access tokens, private SSH key contents, or VM public IP addresses.
5. Prefer small, reviewable Git commits tied to completed steps or verified checkpoints.

Detailed log: [2026-11-04 Azure bootstrap](journal/2026-11-04-azure-bootstrap.md).

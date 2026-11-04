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


## 8. Docker apt keyring directory — command executed, verification pending

The user ran the following command **twice** from the Ubuntu shell:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

It returned to the shell prompt each time without output or reported errors. Silent success is normal for `install -d`; repeating the command is harmless. The next action is to check the directory and its permissions using:

```bash
ls -ld /etc/apt/keyrings
```

**Verification complete:** `ls -ld /etc/apt/keyrings/` returned `drwxr-xr-x 2 root root 4096 Mar 31 2024 /etc/apt/keyrings/`. Directory permissions are 0755 and ownership is `root:root`. The directory's 2024 timestamp is consistent with it preexisting today's command; no Docker GPG key or apt source has been configured yet.


## 9. Docker apt signing key — file verified, authenticity pending

User executed:

```bash
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
ls -lh /etc/apt/keyrings/docker.asc
```

Observed listing:

```text
-rw-r--r-- 1 root root 3.8K Nov 4 15:15 /etc/apt/keyrings/docker.asc
```

The file is present with world-readable mode `0644`, suitable for reading by apt. **Fingerprint verified afterward.** Command `gpg --show-keys --fingerprint /etc/apt/keyrings/docker.asc` reported RSA4096 primary key created 2017-02-22, UID `Docker Release (CE deb) <docker@docker.com>`, fingerprint `9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`. This matches documented Docker CE repository key (also reproduced in NVIDIA's Docker setup instructions: https://docs.nvidia.com/ai-enterprise/deployment/vmware/latest/kubernetes.html). The command also created the local `~/.gnupg` directory/keybox, which is expected and not an error. Key file permissions were already readable (`0644`), so no chmod was needed. No Docker apt source or Docker Engine has been installed yet.


## 10. Docker APT repository configuration — verified

The user executed the Docker Ubuntu deb822 repository configuration command, which wrote `/etc/apt/sources.list.d/docker.sources`. The output was intentionally suppressed with `> /dev/null`. Subsequent inspection:

```bash
cat /etc/apt/sources.list.d/docker.sources
```

Observed content:

```text
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
```

**Result:** The repository configuration is correctly formed for Ubuntu 24.04 (`noble`) on x86-64 and refers to the previously verified Docker signing key. **Pending:** `sudo apt update` to confirm that APT can fetch repository metadata and validate signatures. Docker Engine has not yet been installed.


## 11. Docker repository connectivity — verified

The user executed:

```bash
sudo apt update
```

Observed output included:

```text
Get:5 https://download.docker.com/linux/ubuntu noble InRelease [48.5 kB]
Get:6 https://download.docker.com/linux/ubuntu noble/stable amd64 Packages [73.4 kB]
Fetched 122 kB
Reading package lists... Done
All packages are up to date.
```

**Outcome:** Docker APT metadata was fetched successfully, with no signature or repository errors reported. This verifies package-source connectivity, **not Docker Engine installation**. Next proposed command will show the package installation plan and confirmation prompt for official Docker Engine components: `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, and `docker-compose-plugin`.


## 12. Docker Engine package installation — completed; runtime verification pending

The user executed the official Docker package install command and confirmed the APT prompt:

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**APT transaction:** `0 upgraded, 7 newly installed, 0 to remove, 0 not upgraded`; downloaded 102 MB; projected additional disk usage 389 MB. The user entered `y` at the confirmation prompt.

Installed packages and versions observed in the log:

| Package | Version |
| --- | --- |
| `docker-ce` | `5:29.9.3-1~ubuntu.24.04~noble` |
| `docker-ce-cli` | `5:29.9.3-1~ubuntu.24.04~noble` |
| `containerd.io` | `2.4.2-3~ubuntu.24.04~noble` |
| `docker-buildx-plugin` | `0.38.1-1~ubuntu.24.04~noble` |
| `docker-compose-plugin` | `5.7.0-1~ubuntu.24.04~noble` |
| `docker-ce-rootless-extras` | `5:29.9.3-1~ubuntu.24.04~noble` |
| `pigz` | `2.8-1` |

`docker.service`, `docker.socket`, and `containerd.service` systemd symlinks were created. Package installation returned to the Ubuntu shell prompt with no displayed errors. The package scan reported running kernel up to date; some unrelated service restarts were deferred.

**Important verification boundary:** Successful APT package installation and creation of systemd symlinks do **not** prove Docker daemon readiness. Next command, not yet executed:

```bash
sudo docker version
```

Check both **Client** and **Server** sections; only then record daemon/CLI connectivity as verified. No container has been run and NVIDIA Triton has not yet been installed.


## 13. Docker daemon and CLI communication — verified

Executed from Ubuntu SSH terminal:

```bash
sudo docker version
```

Observed client and server details:

| Component | Reported value |
| --- | --- |
| Docker Client | Docker Engine - Community 29.9.3 |
| Docker Server | Docker Engine - Community 29.9.3 |
| API | 1.56 (server minimum 1.40) |
| OS/architecture | linux/amd64 |
| containerd | v2.4.2 |
| runc | 1.5.2 |
| docker-init | 0.19.0 |
| Experimental | false |

**Result:** Both Client and Server sections are present; the Docker CLI can communicate with the running daemon. This verifies runtime connectivity, not successful execution of a container.

**Next proposed action, pending:** `sudo docker run --rm hello-world`. This downloads a small public test image if necessary, runs a container, and removes the container on exit; the image remains cached until explicitly removed.


## 14. First Docker container — completed

The user ran on the personal Azure Ubuntu VM:

```bash
sudo docker run --rm hello-world
```

Observed output confirmed:
- Image `hello-world:latest` was not previously cached.
- Docker pulled the official public image from Docker Hub, selecting architecture `amd64`.
- Layers completed download and the image was reported downloaded.
- Docker created the test container and streamed its standard output.
- The container printed:

```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

- The shell prompt returned without reported errors.

**Outcome:** Image pulling, daemon access, container creation, and container execution have been demonstrated on the VM. The `--rm` option removes the exited container; the downloaded image normally remains cached locally. This is not yet evidence that NVIDIA Triton or an ML model works.

**Next phase (pending):** Verify Docker storage and select an official NVIDIA Triton container with ONNX backend support and a CPU-compatible open-source vision model. Inspect supported image tags, prerequisites and disk requirements *before* pulling the large image. For CPU inference, avoid assuming GPU-only backends or NVIDIA drivers are available. Keep benchmark outcomes clearly labeled CPU-only.


## 15. Docker storage usage baseline — verified

The user ran:

```bash
sudo docker system df
```

Observed:

```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          1         0         36.94kB   25.87kB (70%)
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     0         0         0B        0B
```

**Interpretation:** Docker currently has one small cached image and no containers, local volumes or build cache. The successful `hello-world --rm` test left no container behind. This command reports Docker-managed image/container data, **not total host disk capacity**.

**Next verification pending:** `df -h /var/lib/docker` to inspect free space on the filesystem holding the standard Docker data directory (assuming Docker's root is still the default). Docker's actual root path can be confirmed later via `sudo docker info --format '{{.DockerRootDir}}'`. Do not download a large Triton image until the supported CPU-only image, ONNX backend, storage requirements and model compatibility have been checked.


## 16. Docker backing filesystem free-space check — verified

The user executed:

```bash
df -h /var/lib/docker
```

Observed output:

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       123G  2.5G  121G   3% /
```

**Interpretation:** The filesystem containing `/var/lib/docker` is the root ext4 volume, with **121 GiB reported available** and only **3% used** at this checkpoint. This represents host filesystem headroom, not Docker-specific image usage; the last `docker system df` check reported only one tiny cached test image.

**Pending verification:** Query `sudo docker info --format '{{.DockerRootDir}}'` for Docker's configured data root before making assumptions about where all Docker data is stored. Newer Docker installations may also store image data through containerd; inspect filesystem use before pulling large runtime images. No Triton image has been pulled.


## 17. Docker data-root verification — completed

The user executed:

```bash
sudo docker info --format '{{.DockerRootDir}}'
```

Actual output:

```text
/var/lib/docker
```

**Verified:** Docker's configured data root is `/var/lib/docker`. The preceding `df -h /var/lib/docker` result showed **121 GiB available** on its root filesystem. This demonstrates available filesystem space, not the exact space a future container image will consume.

**Image assessment (documentation research, not user execution):** NVIDIA's NGC catalog lists `nvcr.io/nvidia/tritonserver:26.10-py3` (updated 2026-11-02), with ONNX Runtime support and reported compressed image size **9.69 GB**. NVIDIA's Triton Quickstart documents CPU-only execution without the Docker `--gpus` flag. References:
- https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/tritonserver/26.10-py3
- https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/getting_started/quickstart.html

No Triton image download has occurred. Estimated decompressed image, disk/temp consumption and actual runtime resource usage still require observation after pulling. GPU-based backends must not be assumed operational on this CPU-only VM.

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


## 18. Triton registry image manifest access — verified

The user executed:

```bash
sudo docker manifest inspect nvcr.io/nvidia/tritonserver:26.10-py3 > /dev/null && echo "TRITON IMAGE TAG ACCESSIBLE"
```

Observed output:

```text
TRITON IMAGE TAG ACCESSIBLE
```

**Outcome:** The Azure VM can access the NVIDIA NGC registry manifest for the specified image tag. This command **did not download the image** and does not establish that the container starts or that ONNX CPU inference succeeds. The planned next action is to pull this image, accounting for its large compressed and unpacked sizes. At the prior disk check, the host reported **121 GiB** available. Preserve the evidence of actual image download, size, launch, and backend verification separately.


## 19. NVIDIA Triton image pull — completed

The user ran:

```bash
sudo docker pull nvcr.io/nvidia/tritonserver:26.10-py3
```

All reported layers finished downloading (`Pull complete`). Final output:

```text
Digest: sha256:b404f7de5dbeeefe0b17d7d149745a50d0989a25d0d831433b5ba63c716c2fcd
Status: Downloaded newer image for nvcr.io/nvidia/tritonserver:26.10-py3
nvcr.io/nvidia/tritonserver:26.10-py3
```

**Verified:** The official NVIDIA NGC Triton 26.10 image has been pulled to the Docker host. The immutable digest provides precise artifact provenance. **Not yet verified:** actual locally reported image size and disk impact, CPU-only container startup, ONNX Runtime backend loading, or any model inference.

**Next proposed command:** `sudo docker images nvcr.io/nvidia/tritonserver:26.10-py3`. Follow up with host storage and backend checks before launching the server. This is not evidence of a running Triton process or a loaded vision model.


## 20. Triton image size in Docker — verified

After the NVIDIA Triton 26.10 image pull, the user ran:

```bash
sudo docker images nvcr.io/nvidia/tritonserver:26.10-py3
```

Observed Docker 29.9.3 output:

```text
IMAGE                                   ID             DISK USAGE   CONTENT SIZE
nvcr.io/nvidia/tritonserver:26.10-py3   b404f7de5dbe       26.5GB         9.45GB
```

**Outcome:** The local image is present; Docker reports **26.5 GB disk usage** and **9.45 GB content size**. These are Docker-reported image metrics and should not be treated as a precise measurement of the difference in physical filesystem occupancy. The host disk difference has now been measured: before the pull the root filesystem showed **2.5G used / 121G available**, and after the pull **28G used / 96G available**. This is an approximately **25.5 GiB increase** in host-reported used space (rounded), which is not directly identical to Docker's 26.5 GB image metric.

**Not yet demonstrated:** the image can launch without a GPU, the ONNX Runtime backend exists and loads, or inference works.


## 21. Post-pull storage availability — verified

The user executed:

```bash
df -h /var/lib/docker
```

Output:

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       123G   28G   96G  23% /
```

**Result:** The VM has **96 GiB free** on the filesystem containing the Docker data root, compared with **121 GiB before the image pull**. This is suitable initial headroom for a small ONNX vision model and Triton exploratory work. The disk numbers are rounded; Docker-reported image size and filesystem-space delta need not match exactly.

**Next proposed command (not yet executed):** inspect the ONNX Runtime backend directory in the downloaded Triton image using a short-lived container, without opening network ports or running the model server.


## 22. Triton ONNX backend files — verified (not yet loaded)

The user executed:

```bash
sudo docker run --rm --entrypoint /bin/ls nvcr.io/nvidia/tritonserver:26.10-py3 -la /opt/tritonserver/backends/onnxruntime
```

**Observed:** The container ran the `ls` process and returned a directory listing without reported errors. Notable files:

- `libtriton_onnxruntime.so` — Triton ONNX Runtime backend library
- `libonnxruntime.so`, `libonnxruntime.so.1.30.0` symlink — ONNX Runtime library
- `libopenvino_intel_cpu_plugin.so` — OpenVINO CPU plugin
- `libonnxruntime_providers_cuda.so`, `libonnxruntime_providers_tensorrt.so` — GPU-related provider libraries present in image (not proof GPU support on current VM)
- `onnx_test_runner`, `onnxruntime_perf_test` — bundled testing tools
- `ort_onnx_version.txt` — version metadata file (content not yet inspected)

**Interpretation:** Files exist in the Triton container image. This does **not** demonstrate successful ONNX backend initialization, selected execution providers, loaded vision models, or inference. The temporary container did not launch the Triton server and did not publish network ports.

**Next:** Prepare an empty local Triton model repository and test CPU-only Triton startup with localhost-bound endpoints before adding an open-source ONNX object detection model. For this personal learning environment, do not open Triton ports on the public Azure interface or add public NSG rules.


## 23. Triton model repository directory — verified

The user executed on the Azure VM:

```bash
mkdir -p ~/dragonstorm-lab/model_repository && ls -ld ~/dragonstorm-lab/model_repository
```

Observed:

```text
drwxrwxr-x 2 azureuser azureuser 4096 Nov  4 16:13 /home/azureuser/dragonstorm-lab/model_repository
```

**Verified:** The local model repository path exists, is owned by `azureuser` and has mode `0775`. No model was placed in it during this step. The directory listing alone does not prove the directory is empty, only that the directory itself exists.

**Next planned experiment:** Launch the already-downloaded `nvcr.io/nvidia/tritonserver:26.10-py3` container without a GPU, mount the model directory read-only at `/models`, and bind the Triton HTTP port only to `127.0.0.1` on the Azure VM. Startup and health will need separate observation. The image's ONNX backend files were previously inspected but no actual model has been loaded.


## 24. Triton CPU-only container launch request — accepted (server status pending)

The user ran:

```bash
sudo docker run -d --rm \\
  --name triton-cpu \\
  --shm-size=1g \\
  -p 127.0.0.1:8000:8000 \\
  -v "$HOME/dragonstorm-lab/model_repository:/models:ro" \\
  nvcr.io/nvidia/tritonserver:26.10-py3 \\
  tritonserver --model-repository=/models \\
  --allow-grpc=false \\
  --allow-metrics=false
```

Observed Docker command returned container ID:

```text
4cac76c7c2b6c2f1b95f70ecd59c9b102f04c0a2c1b7f0bf01e9732f47933081
```

**Verified:** Docker accepted the detached container creation/start command and returned a container ID. The configuration requests no GPU, mounts the previously created local model repository read-only at `/models`, binds Triton HTTP to the **host loopback interface only** (`127.0.0.1:8000`), disables gRPC/metrics, and provisions a 1 GiB shared-memory area. The `--rm` flag automatically cleans up the container when it stops.

**Crucial limitation:** A container ID alone does **not** establish that Triton is still running, initialized or healthy. No model was loaded or inference observed. Next run `sudo docker ps -a --filter name=triton-cpu` to check state, then inspect logs and the local health endpoint. If `--rm` already deleted an exited container, rerun without `--rm` for troubleshooting after examining the status.


## 25. Triton CPU-only container running state — verified

The user executed:

```bash
sudo docker ps -a --filter name=triton-cpu
```

Observed:

```text
CONTAINER ID   IMAGE                                   COMMAND                  CREATED         STATUS         PORTS                      NAMES
4cac76c7c2b6   nvcr.io/nvidia/tritonserver:26.10-py3   "/opt/nvidia/nvidia_…"   2 minutes ago   Up 2 minutes   127.0.0.1:8000->8000/tcp   triton-cpu
```

**Verified:** Docker reported that the container remained running two minutes after its detached launch. The Triton HTTP container port 8000 was published to **host loopback only**. No GPU was requested in the launch command. However, `docker ps` does not prove the Triton binary is initialized, its ONNX backend can load models, or the HTTP health endpoint is ready.

**Next single command (pending):** `sudo docker logs --tail 100 triton-cpu` to examine startup, any CPU/GPU warnings and model repository scanning. Health endpoint check follows separately.


## 26. Triton CPU startup logs — verified; HTTP readiness pending

User command:

```bash
sudo docker logs --tail 100 triton-cpu
```

Selected observed output:

```text
NVIDIA Release 26.10 (build 77056645)
Triton Server Version 2.74.0
WARNING: The NVIDIA Driver was not detected. GPU functionality will not be available.
I1104 16:16:00.666655 1 cuda_memory_manager.cc:117] "CUDA memory pool disabled"
W1104 16:16:00.666613 1 pinned_memory_manager.cc:273] "Unable to allocate pinned system memory, pinned memory pool will not be available: CUDA driver version is insufficient for CUDA runtime version"
E1104 16:16:00.666832 1 server.cc:248] "CudaDriverHelper has not been initialized."
...
model_repository_path[0]         /models
strict_readiness                 1
...
I1104 16:16:00.667515 1 http_server.cc:5022] "Started HTTPService at 0.0.0.0:8000"
```

Backend and Model tables in the startup logs contained **no entries**. This is consistent with having placed no models in the model repository. The message `Started HTTPService` supports that the Triton HTTP listener started despite nonfatal GPU/CUDA initialization warnings. These logs alone do not prove the HTTP readiness check responds successfully or that any ONNX Runtime inference will work. The `0.0.0.0:8000` bind address is inside the container, whereas `docker ps` previously verified host publication at `127.0.0.1:8000` only.

**Pending next user verification:** `curl -i --max-time 5 http://127.0.0.1:8000/v2/health/ready`. Readiness status should be recorded exactly, including any failure; no loaded-model inference has yet been demonstrated.


## 27. Triton HTTP readiness — verified (CPU-only server)

The user executed on the personal Azure Ubuntu VM:

```bash
curl -i --max-time 5 http://127.0.0.1:8000/v2/health/ready
```

Observed response:

```http
HTTP/1.1 200 OK
Content-Length: 0
Content-Type: text/plain
```

**Verified:** The Triton 2.74.0 server's v2 HTTP readiness endpoint responded with **HTTP 200** via the VM's loopback interface. Together with previous evidence (container `Up`, `Started HTTPService at 0.0.0.0:8000` inside container, host port mapping `127.0.0.1:8000->8000/tcp`), this demonstrates a functioning CPU-only Triton server and locally accessible inference API health endpoint without a detected NVIDIA GPU driver.

**Not yet demonstrated:** model repository has an actual model, ONNX Runtime backend dynamically loads, object detection inference works, request/response correctness, benchmarking, dynamic batching, or production readiness. Empty model and backend tables were observed in startup logs.

**Next intended milestone:** Query the Triton v2 server metadata endpoint locally, then prepare a license-reviewed small ONNX object detection model repository and exercise real inference. Continue to bind any exposed HTTP endpoints to localhost only.

**Cost reminder:** Azure auto-shutdown was disabled for the installation session; stop and verify VM state `Stopped (deallocated)` when finished.


## 28. Triton v2 server metadata — verified

User command:

```bash
curl -sS http://127.0.0.1:8000/v2
```

User-reported response:

```json
{"name":"triton","version":"2.74.0","extensions":["classification","sequence","model_repository","model_repository(unload_dependents)","schedule_policy","model_configuration","system_shared_memory","cuda_shared_memory","binary_tensor_data","parameters","statistics","trace","logging"]}
```

**Verified:** The locally running CPU-only Triton service responds to the V2 server metadata API and identifies itself as Triton **2.74.0**. It advertises listed protocol extensions, including model repository management/configuration, schedule policy and request statistics. **Not yet verified:** actual model loading, ONNX Runtime execution, dynamic batching behavior, throughput, or correct prediction outputs. Advertised extension presence is not proof that individual performance features have been exercised.

**Next pending validation:** Inspect `~/dragonstorm-lab/model_repository` and start preparing a license-checked open-source ONNX object detection model with input/output tensors and CPU device support verified before serving. The Triton container was launched with a read-only bind mount, so changes made to the host repository can be recognized only under supported model loading modes; default `MODE_NONE` startup reads models at initialization. Plan for a controlled restart to load new models and check readiness/logs afterward.


## 29. Clean Triton model repository — verified

The user executed:

```bash
ls -la ~/dragonstorm-lab/model_repository
```

Observed output:

```text
total 8
drwxrwxr-x 2 azureuser azureuser 4096 Nov  4 16:13 .
drwxrwxr-x 3 azureuser azureuser 4096 Nov  4 16:13 ..
```

**Verified:** The Triton model repository was empty when inspected (only the `.` and `..` directory entries). No ONNX model, version folder or `config.pbtxt` has been added yet.

**Next planned task:** Select and independently verify a legitimate permissively licensed object-detection ONNX model with known input tensor shape, output parsing and CPU compatibility before creating its Triton repository layout. The running Triton instance uses `MODE_NONE`; new models will require a controlled restart to load. Maintain one verified user action per turn and document completed steps in GitHub.


## 30. First ONNX detector version directory — verified

The user executed on the Azure Ubuntu VM:

```bash
mkdir -p ~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1 && ls -ld ~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1
```

Observed output:

```text
drwxrwxr-x 2 azureuser azureuser 4096 Nov  4 16:33 /home/azureuser/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1
```

**Verified:** Versioned model directory `~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1` exists, owned by `azureuser`, mode `0775`. This is the conventional Triton model-repository layout; the initial model version directory has been created but **no model download or configuration is demonstrated** by this output. The existing CPU-only Triton instance is already running with `MODE_NONE`, and will need a controlled restart after model files/configuration are added.

**Next planned step:** Download the SSD-MobileNetV1-12 ONNX binary from its upstream distribution URL, confirm final file size and SHA-256, and inspect graph inputs and outputs before generating `config.pbtxt`. Avoid committing binary model artifacts to the public GitHub learning repository.


## 31. Download initial SSD-MobileNet ONNX model — transfer completed, integrity not yet verified

The user ran on the personal Azure VM:

```bash
curl --fail --location --show-error \\
  --output "$HOME/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx" \\
  "https://huggingface.co/onnxmodelzoo/ssd_mobilenet_v1_12/resolve/main/ssd_mobilenet_v1_12.onnx"
```

Observed curl transfer output showed an initial **1,072-byte** response followed by a **28.0M** transfer, with no error and a returned shell prompt. With `--location`, this is consistent with following the model host's redirect and downloading the model artifact. The target path is version 1's standard Triton filename `model.onnx`.

**Evidence boundary:** Curl reported a successful download; exact file integrity, actual local file size and graph compatibility have **not yet been independently verified**. No Triton inference performed. The next verification must run SHA-256 on the local artifact and compare to the upstream model-file metadata (expected `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058` as documented in `docs/models/ssd-mobilenetv1-12-source-notes.md`). Do not restart Triton until model graph and `config.pbtxt` are validated.


## 32. SSD-MobileNet ONNX artifact SHA-256 integrity — verified

On the Azure Ubuntu VM the user executed:

```bash
sha256sum ~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx
```

Observed output:

```text
b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058  /home/azureuser/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx
```

**Verified:** The local `model.onnx` checksum **exactly matches** the previously recorded upstream ONNX Model Zoo / Hugging Face expected SHA-256 `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058`. This verifies the binary's byte integrity relative to that upstream digest; it does **not** guarantee model safety, graph compatibility, or inference correctness. No model has been loaded by Triton yet.

**Next:** Inspect the actual ONNX graph input/output names, dtypes and shapes, and opset using an ONNX parser inside an isolated environment. The existing Triton container has the model repository mounted read-only. If the container lacks the Python `onnx` package, check first and choose a bounded reproducible alternative rather than modifying the running Triton environment.


## 33. Python ONNX parser availability in Triton container — checked

The user executed:

```bash
sudo docker exec triton-cpu python3 -c 'import importlib.util; print("ONNX package installed:", importlib.util.find_spec("onnx") is not None)'
```

Observed output:

```text
ONNX package installed: False
```

**Interpretation:** The Python interpreter found inside the running `triton-cpu` container does **not** have the importable `onnx` Python graph-inspection package installed. This is **not** evidence that the Triton ONNX Runtime backend is unavailable: the separately inspected `/opt/tritonserver/backends/onnxruntime` contains its compiled runtime shared libraries. Parsing model metadata with `onnx` and serving an ONNX model with Triton ONNX Runtime are distinct tasks.

**Approach:** Do not modify the running Triton service or install packages into its ephemeral container. Verify host Python packaging/virtual-environment availability, then use a dedicated isolated inspection environment to report the actual graph input and output tensor names, element types, dimensions and opset. Model loading and inference remain pending.


## 34. Ubuntu host Python inspection environment availability — verified

The user ran:

```bash
python3 -c 'import sys, importlib.util; print("Python:", sys.version.split()[0]); print("pip:", importlib.util.find_spec("pip") is not None); print("venv:", importlib.util.find_spec("venv") is not None); print("onnx:", importlib.util.find_spec("onnx") is not None)'
```

Observed exact output:

```text
Python: 3.12.3
pip: False
venv: True
onnx: False
```

**Verified:** Ubuntu host uses Python **3.12.3**; importable `pip` is absent in that interpreter; the `venv` module can be found; and `onnx` has not yet been installed in host Python. Importable `venv` does **not** prove that a new virtual environment can successfully bootstrap pip; Ubuntu may require a version-specific `python3-venv` package.

**Next single command planned:** `python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect`. If it fails, preserve the error and address missing `ensurepip`/Ubuntu venv packages without modifying the running Triton container or system-wide Python packages. Do not claim ONNX graph inspection complete.


## 35. Virtual environment creation failure — ensurepip missing (verified)

The user ran on the Azure Ubuntu VM:

```bash
python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect
```

Actual failure:

```text
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /home/azureuser/dragonstorm-lab/.venv-onnx-inspect/bin/python3
```

**Status:** The venv creation attempt failed, so no functional isolated environment has been verified. It may have left a partial directory on the host. The missing `ensurepip` capability is consistent with a minimal Ubuntu Python 3.12 installation; this error does not demonstrate any failure of Docker, Triton server readiness, or the downloaded ONNX model.

**Next corrective action pending:** Install distro package `python3.12-venv` with `sudo apt install -y python3.12-venv`, capture package-manager result, then retry `python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect` as a separate checked action. Avoid installing ONNX into the host's externally managed system Python or mutating the live Triton container.


## 36. Install Python 3.12 venv bootstrap support — verified

Following a failed virtual environment creation (`ensurepip` unavailable), the user executed:

```bash
sudo apt install -y python3.12-venv
```

APT successfully installed three previously absent packages:

```text
python3-pip-whl       24.0+dfsg-1ubuntu1.3
python3-setuptools-whl 68.1.2-2ubuntu1.2
python3.12-venv      3.12.3-1ubuntu0.17
0 upgraded, 3 newly installed, 0 to remove and 0 not upgraded.
Fetched 2429 kB
After this operation, 2777 kB of additional disk space will be used.
Setting up python3-setuptools-whl ...
Setting up python3-pip-whl ...
Setting up python3.12-venv ...
Running kernel seems to be up-to-date.
No containers need to be restarted.
```

APT's `needrestart` scan reported some deferred service restarts (`dbus`, `networkd-dispatcher`, `systemd-logind`, `unattended-upgrades`); it also identified the user's current SSH process as using outdated binaries. These are observations, not evidence of a failing Python install or reason to immediately disrupt the SSH session. No Docker container restart was requested.

**Verified:** Ubuntu Python 3.12 venv bootstrap dependency has been installed successfully. **Not yet verified:** creation and operation of the dedicated ONNX inspection virtual environment. Next run `python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect` again and inspect the actual outcome. The previous failed attempt may have left a partial directory, so verify the new result rather than assuming success.


## 37. Recreated Python virtual environment after installing support — command completed without errors

After installing Ubuntu package `python3.12-venv`, the user ran the same command twice in the Azure VM terminal:

```bash
python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect
python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect
```

Both commands returned directly to the shell prompt, with **no terminal output or error messages**. The normal successful `venv` behavior is to emit no output. Re-running `venv` with an existing target directory is typically harmless; it does not automatically clear the directory unless special options are used.

**Verified checkpoint:** The prior `ensurepip` error did not recur, and both attempted environment-creation commands completed without a reported error. **Still pending:** direct verification that the virtual environment's Python executable and `pip` work. This avoids treating a silent command as proof all tools are installed.

**Next user command:** `~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m pip --version`. Once verified, install the ONNX parser into this **isolated venv**, not into system Python or the Triton server container; inspect actual model graph metadata before writing `config.pbtxt`.


## 38. Python and pip inside isolated ONNX inspection venv — verified

The user ran:

```bash
~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m pip --version
```

Observed exact output:

```text
pip 24.0 from /home/azureuser/dragonstorm-lab/.venv-onnx-inspect/lib/python3.12/site-packages/pip (python 3.12)
```

**Verified:** The venv-local Python interpreter successfully invokes `pip 24.0` from the virtual environment's Python 3.12 site-packages. The previous missing-`ensurepip` blocker has been resolved by installing `python3.12-venv` and recreating the environment. No dependency install inside the venv or ONNX graph inspection has yet been demonstrated.

**Next single action (pending):** Install an explicitly version-pinned ONNX Python parser (`onnx==1.19.1`) using `~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m pip install 'onnx==1.19.1'`. This preserves separation from system Python and the already running CPU-only Triton container; validate installation from the user's output before inspecting real input/output tensor metadata.


## 39. Isolated ONNX graph parser installation — verified

User executed on the Azure VM:

```bash
~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m pip install 'onnx==1.19.1'
```

Package manager reported successful installation:

```text
Successfully installed ml_dtypes-0.6.0 numpy-2.5.4 onnx-1.19.1 protobuf-7.36.2 typing_extensions-4.16.0
```

**Verified:** ONNX 1.19.1 and its resolved dependencies installed successfully into the preexisting Python 3.12 virtual environment `.venv-onnx-inspect`. The observed wheel was `onnx-1.19.1-cp312-cp312-manylinux2014_x86_64`, consistent with this Linux x86_64 Python 3.12 host. The operation did not target the running Triton container or global system Python.

**Reproducibility note:** Only `onnx` was explicitly pinned; dependencies were resolved to the listed versions by pip at installation time. For future exact reproducibility, capture an environment lock/freeze separately and keep records in GitHub without committing the local venv files.

**Next verification pending:** Parse `~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx` with the isolated ONNX parser, extract actual inputs/outputs, their dtypes and dimensions, opset and run `onnx.checker.check_model`. This installation outcome alone does not prove the ONNX graph is valid, the Triton backend loads, or inference works.


## 40. ONNX graph inspection and checker — verified

The user executed the previously recorded Python heredoc with isolated `onnx==1.19.1`, `onnx.load` and `onnx.checker.check_model` on the SHA-256-verified model at `~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx`.

Observed exact output:

```text
ONNX version: 1.19.1
IR version: 7
Opsets: [('', 12)]

INPUTS:
  inputs: dtype=UINT8, shape=['unk__6578', 'unk__6579', 'unk__6580', 3]

OUTPUTS:
  detection_boxes: dtype=FLOAT, shape=['unk__6581', 'unk__6582', 4]
  detection_classes: dtype=FLOAT, shape=['unk__6583', 'unk__6584']
  detection_scores: dtype=FLOAT, shape=['unk__6585', 'unk__6586']
  num_detections: dtype=FLOAT, shape=['unk__6587']

ONNX GRAPH CHECK: PASSED
```

**Verified:** ONNX graph IR 7, opset 12, exact input and output tensor names, ONNX element types, symbolic dimensions and graph checker acceptance. The graph's input is rank 4 UINT8 NHWC (last dimension exactly 3); output detections carry FP32 data. The `unk__*` dimensions are *independent symbolic names* in the observed model and have not been proven equal across tensors; use a distinct `-1` for each symbolic dimension in Triton config. **Important:** These observed graph tensor names differ from names in the historic model documentation. Favor inspected binary metadata over the older descriptions.

**Configuration artifact committed (not deployed yet):** `model_repository/ssd_mobilenet_v1_12/config.pbtxt` with `backend: "onnxruntime"`, `max_batch_size: 0`, UINT8 input dims `[-1,-1,-1,3]`, FP32 output dims `[-1,-1,4]`, `[-1,-1]`, `[-1,-1]`, `[-1]`, and a single `KIND_CPU` instance. Config uses no Triton-managed batching; full ONNX batch dimension is retained as an explicit dimension of each tensor. This is an initial hypothesis consistent with graph metadata, **not** yet evidence the ONNX Runtime backend can load or infer.

**Next user action (pending):** Download the committed config file onto the personal VM next to the model's version directory; inspect content afterward, then controlled restart of Triton because the running server was started in `MODE_NONE`. Keep host HTTP bound to loopback and document any model-load errors.


## 41. Triton model configuration transferred to Azure VM — curl completed; contents pending validation

The user ran:

```bash
curl --fail --location --show-error \\
  --output "$HOME/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/config.pbtxt" \\
  "https://raw.githubusercontent.com/ashutoshsingh1501-meta/dragonstorm-ml-engineering/main/model_repository/ssd_mobilenet_v1_12/config.pbtxt"
```

Observed curl progress: `100 1069 100 1069` bytes received with no reported error and returned shell prompt.

**Verified:** Download command successfully transferred approximately 1,069 bytes into the intended local Triton model-configuration path, sourced from the version-controlled project configuration. **Not yet verified:** The actual content saved in the file, its exact match to the GitHub file, the config's acceptance by Triton, or model loading. The previously running Triton server is still using `MODE_NONE` and has **not** been restarted as part of this step.

**Next checkpoint:** Review contents of `~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/config.pbtxt` with `cat` before a controlled restart. For exact provenance, a checksum comparison can be added after verifying content, but no hash was observed in this user response. Continue local-only network exposure.


## 42. Azure VM Triton configuration inspected — verified by contents

The user ran:

```bash
cat ~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/config.pbtxt
```

The displayed file agrees with the committed source at `model_repository/ssd_mobilenet_v1_12/config.pbtxt` in all critical configuration fields:

- `name: "ssd_mobilenet_v1_12"`, `backend: "onnxruntime"`, and `max_batch_size: 0` (no Triton-managed dynamic batching).
- Input `inputs`, `TYPE_UINT8`, `dims: [-1, -1, -1, 3]`.
- Four outputs all `TYPE_FP32`: `detection_boxes [-1, -1, 4]`, `detection_classes [-1, -1]`, `detection_scores [-1, -1]`, `num_detections [-1]`.
- One CPU execution instance, `instance_group { count: 1 kind: KIND_CPU }`.
- Source provenance comment records model SHA-256 `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058`.

**Evidence boundary:** This is verification of displayed file contents, not a byte-for-byte comparison of local vs. GitHub hashes and not Triton config parser or runtime acceptance. The original Triton 2.74.0 server was started in `MODE_NONE` with an empty repository and remains running from the preceding checkpoints. The ONNX model and configuration were created after startup. The next step should stop the old server in a controlled manner; `--rm` removes the stopped container. Then launch again with the same localhost-only port and mounted model repository, verify model load logs and readiness separately, and troubleshoot any CPU-provider load errors.


## 43. Controlled stop of first empty-repository Triton server — verified

The user executed:

```bash
sudo docker stop triton-cpu
```

Output:

```text
triton-cpu
```

**Verified:** Docker acknowledged the controlled stop of the previously running `triton-cpu` container. It had been launched with `--rm`, so container auto-removal is expected after stopping, but a separate `docker ps -a` check was not performed. The pulled image remains in the Docker cache, and the ONNX artifact/config reside in the host bind-mounted model repository, outside the deleted/stopped container.

**Reason:** Triton was launched with `model_control_mode=MODE_NONE` while the model repository was empty. New ONNX model and `config.pbtxt` have since been added and visually checked; Triton must be restarted to scan and load them. No actual backend/model load is yet verified. Recreate the container with `127.0.0.1:8000:8000`, no GPU, read-only host model mount; collect the returned container ID, inspect `docker ps`, logs, model readiness and inference in separate verified steps.

**Cost note:** Azure auto-shutdown remains Off during this session. Manually stop/deallocate the VM before ending and confirm `Stopped (deallocated)` in Azure Portal; an SSH container stop is not a VM stop.


## 44. Model-enabled Triton container launch request — Docker accepted, model load pending

The user executed:

```bash
sudo docker run -d \\
  --name triton-cpu \\
  --shm-size=1g \\
  -p 127.0.0.1:8000:8000 \\
  -v "$HOME/dragonstorm-lab/model_repository:/models:ro" \\
  nvcr.io/nvidia/tritonserver:26.10-py3 \\
  tritonserver --model-repository=/models \\
  --allow-grpc=false \\
  --allow-metrics=false
```

Docker returned container ID:

```text
897812b33ddebe91705ba30b1f3f9d723baff19b7544e1d63e20085c5ff65afe
```

**Verified:** Docker accepted the detached container launch command and returned an ID. Unlike the earlier launch, `--rm` is omitted to **retain the container and logs after failure** for troubleshooting. The host model repository now contains model version 1's `model.onnx` (prior checksum verified) and `config.pbtxt` (contents previously inspected), mounted read-only at `/models`. The Docker port mapping binds HTTP only to the host's loopback interface, and no GPU request was made.

**Unverified:** Whether container remains running, the ONNX Runtime backend loads the model, model readiness, or any successful inference. Do not equate a returned container ID with successful server initialization.

**Next single command:** `sudo docker ps -a --filter name=triton-cpu`. Then inspect `sudo docker logs --tail 150 triton-cpu` (possibly longer if needed) to determine backend/model load, including any failures. For any failure, preserve logs and troubleshoot before retrying. This VM's Azure auto-shutdown remains Off; at session end verify `Stopped (deallocated)` in portal.

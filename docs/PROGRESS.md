# Engineering Progress Tracker

This file records **verified outcomes only**. Planned actions are explicitly marked pending. For detailed commands and evidence, follow the dated journal.

## Current milestone — 2026-11-06

**Stage:** Day 1 Docker/Triton CPU ONNX model load and model-specific HTTP readiness **verified**, actual image inference **pending**. Day 1 Azure Stop (deallocate) **verified**; Day 2 VM Start completed (**Running**). SSH verified; Docker container confirmed stopped with exit code 0. Triton restart and model readiness after VM reboot not yet verified. [Day 2 journal](journal/2026-11-06-day-2.md).

| ID | Milestone | Status | Evidence |
| --- | --- | --- | --- |
| D2-01 | Azure VM started for Day 2 | Complete | Azure Portal success toast and Overview status `Running` for `vm-dragonstorm-ml-01` on 2026-11-06; guest-agent status showed transient/unverified warning |
| D2-02 | Re-establish secure SSH session | Complete | User's Windows PowerShell screenshot showed a successful Ubuntu shell login to the lab VM |
| D2-02a | Review Azure Advisor VMSS Flex suggestion | Complete (no migration) | Azure Advisor Reliability/Medium suggested migrating standalone VM to VM Scale Sets Flex; this is an optional HA/scale recommendation, not a required change for a personal single-VM CPU inference lab; defer without provisioning extra VMs |
| D2-03 | Inspect/resume Triton Docker container | In progress | `sudo docker ps -a --filter name=triton-cpu` shows retained container `897812b33dde`, `Exited (0) 32 hours ago` after prior Azure deallocation; restart and readiness pending |
| D2-04 | Recheck model-specific HTTP readiness | **Pending** | Verify `/v2/models/ssd_mobilenet_v1_12/ready` on localhost after service restart |
| D2-05 | First actual model inference | **Pending** | Send UINT8 NHWC image tensor and inspect output tensors before any accuracy/performance claims |
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
| I-17a | Triton image registry manifest | Complete | `sudo docker manifest inspect nvcr.io/nvidia/tritonserver:26.10-py3` succeeded; tag accessible |
| I-17b | Triton image pull | Complete | `docker pull nvcr.io/nvidia/tritonserver:26.10-py3` succeeded; digest `sha256:b404f7de5dbeeefe0b17d7d149745a50d0989a25d0d831433b5ba63c716c2fcd` |
| I-17c | Triton image local size | Complete | Docker 29.9.3 `images` reports image ID `b404f7de5dbe`, disk usage 26.5 GB, content size 9.45 GB |
| I-17c-1 | Host free space after Triton pull | Complete | `df -h /var/lib/docker` reports `/dev/root` 123G total, **28G used**, **96G available**, 23% used (before pull 2.5G used / 121G free) |
| I-17c-2 | Triton ONNX backend image inspection | Complete | Short-lived `docker run --rm --entrypoint /bin/ls ... -la /opt/tritonserver/backends/onnxruntime` listed ONNX backend shared libraries, OpenVINO CPU plugin, test tools; backend startup not yet tested |
| I-17e | Triton model repository directory | Complete | `mkdir -p ~/dragonstorm-lab/model_repository && ls -ld ...` confirmed path, `azureuser` ownership, mode 0775; no model loaded yet |
| I-17d | Triton server CPU launch | Complete | Detached CPU-only container reported `Up 2 minutes`; Triton 2.74.0 HTTPService started and `/v2/health/ready` returned HTTP 200; model/backends not loaded |
| I-17d-1 | Triton container launch accepted | Complete | `sudo docker run -d --rm --name triton-cpu ...` returned container ID prefix `4cac76c7c2b6`; no GPU requested; port 8000 bound to host localhost; read-only model mount |
| I-17d-2 | Triton container running state | Complete | `sudo docker ps -a --filter name=triton-cpu`: container `4cac76c7c2b6` `Up 2 minutes`, HTTP port `127.0.0.1:8000->8000/tcp`; Triton health not yet checked |
| I-17d-3 | Triton startup logs | Complete | Logs show NVIDIA Release 26.10, Triton 2.74.0, `Started HTTPService at 0.0.0.0:8000`; missing NVIDIA driver/CUDA warnings, no models/backends loaded |
| I-17d-4 | Triton HTTP health | Complete | `curl -i --max-time 5 http://127.0.0.1:8000/v2/health/ready`: `HTTP/1.1 200 OK`, Content-Length: 0; Triton readiness verified, no inference tested |
| I-17d-4 | Triton HTTP health | **Pending** | Inspect localhost `/v2/health/ready` after logs confirm startup |
| I-17d-5 | Triton v2 metadata endpoint | Complete | `curl -sS http://127.0.0.1:8000/v2` returned name `triton`, version `2.74.0`, and V2 extensions including model_repository, model_configuration, statistics and schedule_policy |
| I-18a | Initial model repository listing | Complete | `ls -la ~/dragonstorm-lab/model_repository` contained only `.` and `..`, confirming the directory was empty before adding any model |
| I-18b | First ONNX detector selection | **Pending** | Verify open-source license, source files, ONNX input/output structure and CPU inference suitability before download |
| I-18c | First ONNX model versioned directory | Complete | `mkdir -p ~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1 && ls -ld ...` verified `/home/azureuser/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1`, owner/group `azureuser`, mode 0775; model binary not downloaded |
| I-18d | ONNX model artifact download | Complete (integrity pending) | `curl --fail --location --show-error --output .../ssd_mobilenet_v1_12/1/model.onnx` transferred about 28.0 MiB from the ONNX Model Zoo Hugging Face resolve URL without reported errors; SHA-256 not yet checked |
| I-18e | ONNX model artifact SHA-256 | Complete | Local SHA-256 exactly matches upstream metadata: `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058` |
| I-18f | ONNX graph metadata inspection | **Pending** | Container Python `onnx` package absent; inspect host Python package / venv capabilities then create isolated model inspection environment to inspect actual tensors and opset |
| I-18f-1 | Triton container Python ONNX parser check | Complete | `sudo docker exec triton-cpu python3 -c 'import importlib.util; ...'` printed `ONNX package installed: False`; Triton ONNX Runtime shared-library backend remains present |
| I-18f-2 | Ubuntu Python inspection tools | Complete | Host Python 3.12.3; `pip=False`, `venv=True`, `onnx=False` via `importlib.util.find_spec`; venv creation not yet tested |
| I-18f-3 | Isolated ONNX inspection venv creation | Complete (operational check pending) | After `python3.12-venv` installation, user ran `python3 -m venv ~/dragonstorm-lab/.venv-onnx-inspect` twice; both returned to prompt without error/output; interpreter and pip verification pending |
| I-18f-5 | Verify isolated Python and pip | Complete | `~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m pip --version` returned `pip 24.0` from venv-local `lib/python3.12/site-packages/pip` |
| I-18f-6 | Install isolated ONNX parser | Complete | `.venv-onnx-inspect/bin/python -m pip install 'onnx==1.19.1'` succeeded; installed onnx 1.19.1, numpy 2.5.4, protobuf 7.36.2, ml_dtypes 0.6.0, typing_extensions 4.16.0 |
| I-18f-7 | Inspect ONNX graph and validate schema | Complete | onnx 1.19.1: IR 7, opset 12; input `inputs` UINT8 symbolic NHWC rank 4 (last dimension 3); outputs `detection_boxes` FLOAT [?,?,4], `detection_classes` FLOAT [?,?], `detection_scores` FLOAT [?,?], `num_detections` FLOAT [?]; ONNX checker PASSED |
| I-18g | Commit initial Triton model config to GitHub | Complete (VM validation pending) | `model_repository/ssd_mobilenet_v1_12/config.pbtxt` committed with exact observed tensor names/types, max_batch_size 0, one KIND_CPU instance |
| I-18h | Copy Triton config to Azure VM | Complete (contents pending verification) | `curl --fail --location --show-error --output .../ssd_mobilenet_v1_12/config.pbtxt` retrieved 1,069 bytes from GitHub raw URL without reported error; contents not yet inspected |
| I-18i | Validate VM Triton config against GitHub | Complete (visual inspection) | User `cat` output matches the committed config fields: `ssd_mobilenet_v1_12`, onnxruntime, max_batch_size 0, UINT8 input `inputs`, four FP32 outputs, KIND_CPU x1; runtime load not yet checked |
| I-18j | Controlled stop of empty Triton server | Complete | `sudo docker stop triton-cpu` returned `triton-cpu` successfully; stopped before model-enabled relaunch; auto-removal expected via `--rm` but not independently checked |
| I-18k | First model-enabled Triton launch | Complete (container ID returned) | `sudo docker run -d --name triton-cpu ...` returned container ID `897812b33dde...65afe`; no `--rm`, port bound to 127.0.0.1:8000, model repository mounted read-only, no GPU requested; running state and model load still pending |
| I-18l | Verify model-enabled container status | Complete | `sudo docker ps -a --filter name=triton-cpu` shows ID `897812b33dde`, Up 3 minutes, `127.0.0.1:8000->8000/tcp`; backend/model readiness still unverified |
| I-18l-1 | Verify model-enabled startup logs | Complete | `sudo docker logs --tail 150 triton-cpu` confirms `TRITONBACKEND_Initialize: onnxruntime`, instance initialized on `CPU device 0`, `successfully loaded 'ssd_mobilenet_v1_12'`, model 1 READY, HTTPService started |
| I-18m-1 | Check model-specific HTTP readiness | Complete | `curl -i --max-time 10 http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready` returned `HTTP/1.1 200 OK`, Content-Length: 0; model ready on localhost; no inference completed |
| I-18n | End-of-session Azure VM deallocation | Complete | User-supplied Azure Portal Overview screenshot explicitly shows `vm-dragonstorm-ml-01` status **Stopped (deallocated)**; compute deallocation verified for end of Day 1; Azure disk/network costs may persist |
| I-18m-2 | Model inference functional test | **Pending** | Perform real CPU inference with controlled image tensor, verify prediction tensors and output interpretation; not established by startup logs |
| I-18m | Verify ONNX CPU model load | **Pending** | Inspect Triton logs, then model-specific readiness and actual inference separately |
| I-18f-4 | Install Ubuntu Python 3.12 venv support | Complete | `sudo apt install -y python3.12-venv`: installed python3.12-venv 3.12.3-1ubuntu0.17, python3-pip-whl 24.0+dfsg-1ubuntu1.3, python3-setuptools-whl 68.1.2-2ubuntu1.2; no containers require restart |
| I-18 | Vision inference | **Pending** | No model or inference evidence |

## Open verification items

- Independently verify the SSH host key fingerprint via a trusted out-of-band channel; the first SSH host key was accepted before this verification.
- Verify active network rule and power state before each remote connection; public client IP may change.
- **2026-11-04 shutdown verified:** Azure Portal screenshot confirms VM `vm-dragonstorm-ml-01` reached **Stopped (deallocated)** after the session. Auto-shutdown was left Off during testing; re-enable automatic shutdown before subsequent unattended use. Storage and certain network resources can still incur cost.
- Reassess image backend support, actual container size, and cost prior to downloading Triton.
- Keep GPU provisioning separate; current deployment is CPU-only.

## Documentation rules

1. For **each executed command or Azure configuration step**, record the exact action (with secrets removed), observed outcome, and any errors in the journal.
2. Update the tracker only **after** the result is reported/verified; never mark an intention as complete.
3. Note decision rationale, costs, reproducibility and rollback when relevant.
4. Never publish personal contact details, subscription IDs, access tokens, private SSH key contents, or VM public IP addresses.
5. Prefer small, reviewable Git commits tied to completed steps or verified checkpoints.

Detailed log: [2026-11-04 Azure bootstrap](journal/2026-11-04-azure-bootstrap.md).

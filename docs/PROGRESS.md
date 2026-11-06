# Engineering Progress Tracker

This file records **verified outcomes only**. Planned actions are explicitly marked pending. For detailed commands and evidence, follow the dated journal.

## Current milestone — 2026-11-06

**Stage:** Day 1 Docker/Triton CPU ONNX model load and model-specific HTTP readiness **verified**, actual image inference **pending**. Day 1 Azure Stop (deallocate) **verified**; Day 2 VM Start completed (**Running**). SSH and existing Triton container restart verified; container Up About a minute with localhost HTTP mapping. Model-specific HTTP readiness verified (200 OK) after VM reboot; first inference still pending. [Day 2 journal](journal/2026-11-06-day-2.md).

| ID | Milestone | Status | Evidence |
| --- | --- | --- | --- |
| D2-01 | Azure VM started for Day 2 | Complete | Azure Portal success toast and Overview status `Running` for `vm-dragonstorm-ml-01` on 2026-11-06; guest-agent status showed transient/unverified warning |
| D2-02 | Re-establish secure SSH session | Complete | User's Windows PowerShell screenshot showed a successful Ubuntu shell login to the lab VM |
| D2-02a | Review Azure Advisor VMSS Flex suggestion | Complete (no migration) | Azure Advisor Reliability/Medium suggested migrating standalone VM to VM Scale Sets Flex; this is an optional HA/scale recommendation, not a required change for a personal single-VM CPU inference lab; defer without provisioning extra VMs |
| D2-03 | Inspect/resume Triton Docker container | In progress | After initially verifying retained container `897812b33dde` as Exited (0), `sudo docker start triton-cpu` returned `triton-cpu`; running state and model HTTP readiness not yet checked |
| D2-03a | Confirm Triton running after restart | Complete | `sudo docker ps -a --filter name=triton-cpu` showed existing `897812b33dde` container **Up About a minute**, HTTP host mapping `127.0.0.1:8000->8000/tcp`; model-specific readiness pending |
| D2-04 | Recheck model-specific HTTP readiness | Complete | After Azure VM cold start and Docker restart, `curl -i --max-time 10 http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready` returned `HTTP/1.1 200 OK`, `Content-Length: 0` |
| D2-04a | Inspect V2 live model metadata | Complete | `GET /v2/models/ssd_mobilenet_v1_12`: name `ssd_mobilenet_v1_12`, version 1, platform `onnxruntime_onnx`; `inputs` UINT8 [-1,-1,-1,3]; FP32 outputs: boxes [-1,-1,4], classes [-1,-1], scores [-1,-1], num_detections [-1]; consistent with graph/config |
| D2-04b | Author reproducible first V2 inference smoke client | Complete (authored, not executed) | `scripts/first_triton_inference.py` committed; synthetic black 1x300x300x3 UINT8, V2 binary tensor request, FP32 output decoding; API execution still pending |
| D2-04c | Download smoke client to Azure VM | Complete (transfer observed) | `curl --fail --location --show-error` downloaded 5,041 bytes to `~/dragonstorm-lab/first_triton_inference.py` without reported errors; local file syntax and hash not yet validated |
| D2-04d | Syntax-check downloaded inference client | Complete | `~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m py_compile ~/dragonstorm-lab/first_triton_inference.py` succeeded; shell printed `PYTHON SYNTAX CHECK: PASSED`; no inference ran |
| D2-04e | First Triton V2 CPU inference smoke test | Complete | Executed `first_triton_inference.py` in isolated venv: HTTP 200; UINT8 [1,300,300,3] 270000-byte payload; four FP32 tensors decoded (boxes [1,100,4], classes [1,100], scores [1,100], count [1]); all finite; count 0 on synthetic black input; SMOKE TEST PASSED |
| D2-06 | Verify real-photo input dependencies | Complete | Isolated Python 3.12 venv `importlib.util.find_spec('PIL')` returned False; Pillow not installed; actual image decoding/inference pending |
| D2-07 | Install isolated Pillow decoder | Complete (pip installation) | Venv-local `python -m pip install 'Pillow==11.3.0'` downloaded Linux Python 3.12 wheel (6.6 MB) and reported `Successfully installed Pillow-11.3.0`; runtime import pending |
| D2-07a | Verify Pillow import and version | Complete | User ran venv-local Python `import PIL`; `Pillow version: 11.3.0` and module path `/home/azureuser/dragonstorm-lab/.venv-onnx-inspect/lib/python3.12/site-packages/PIL/__init__.py` |
| D2-08 | Download public test photograph | Complete (curl transfer) | `curl --fail --location --show-error` downloaded approximately 645 KB from PyTorch Hub `images/dog.jpg` to `~/dragonstorm-lab/test-dog.jpg` without reported error; image format and decode unverified |
| D2-08a | Validate downloaded test photo with Pillow | Complete | Pillow `Image.open().load()` succeeded: JPEG, size (1546,1213), RGB mode, converted RGB mode, printed `IMAGE DECODE: PASSED` |
| D2-08b | Verify first photo preprocessing tensor | Complete | Pillow RGB JPEG resize 300×300 BILINEAR and NumPy expand_dims produced UINT8 [1,300,300,3], 270000 bytes, pixel min 1 max 255, 270000 nonzero, `IMAGE PREPROCESSING: PASSED`; stretch can distort aspect ratio |
| D2-08c | Author real-photo inference script | Complete (not run) | `scripts/real_photo_triton_inference.py` committed with Pillow RGB resize [1,300,300,3], binary Triton inference request, four FP32 tensor validation and top-5 raw score summary; runtime test pending |
| D2-08d | Download real-photo inference script to VM | Complete (transfer verified) | User's `curl --fail --location --show-error` transferred exactly 5,867 bytes to `~/dragonstorm-lab/real_photo_triton_inference.py`; no reported error; syntax/runtime untested |
| D2-08e | Syntax-check real-photo inference script | Complete | User executed venv-local Python `-m py_compile ~/dragonstorm-lab/real_photo_triton_inference.py`; shell printed `REAL PHOTO SCRIPT SYNTAX: PASSED` |
| D2-08f | First real-photo Triton CPU inference | **Pending** | Execute syntax-verified script on dog JPEG and inspect HTTP response, four FP32 tensors, raw detection scores/classes/boxes; quality not yet validated |
| D2-05 | First actual model inference | Complete (synthetic smoke test only) | CPU inference POST succeeded on deterministic black image; returned four correctly decoded FP32 tensors; real-photo object detection and accuracy remain pending |
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

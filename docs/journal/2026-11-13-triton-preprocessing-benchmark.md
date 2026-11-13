# Triton serving, preprocessing and benchmark lab — November 12–13, 2026

**Source of evidence:** User-provided Azure VM terminal outputs and inspected annotated JPEG. This journal records *observed* checks, commands, interpretations, and remaining uncertainties. Scripts created on the VM during the session are reproduced in `scripts/`; remote GitHub addition does not imply that copies on the VM were committed.

## November 7 handoff and November 12 recovery

- Prior Day 3: downloaded `annotate_triton_detection.py` (5,569 bytes); isolated Python `-m py_compile` printed `ANNOTATION SCRIPT SYNTAX: PASSED`. SSH session closed; Azure screenshot showed **Stopped (deallocated)** at previous close.
- November 12: SSH to the previously used address failed repeatedly with `Connection refused`. Both key-file path variants failed; the client had not reached key authentication.
- Azure **Run Command / RunShellScript** executed `hostname`, `uptime`, `systemctl status ssh`, `ss -lntp | grep ':22'`, `journalctl -u ssh -n 30`, `ufw status`. Hostname matched; `ssh.service` was inactive with `ssh.socket` active and systemd listening on TCP 22; UFW inactive.
- Ran `sudo systemctl start ssh.service` and checked `systemctl is-active ssh.service`, `ss -lntp`, `/usr/sbin/sshd -t`: **active**, SSH daemon listening on IPv4/IPv6 22, config **VALID**. Remote SSH still refused.
- **Actual resolution:** user updated Azure NSG inbound SSH source to **My IP Address** after their local public IP changed. Subsequent `ssh -i ... azureuser@<VM-public-IP>` succeeded. Do not publish the private key or fixed public IP in this repository. Avoid claiming inactive `ssh.service` was the root cause; systemd socket activation was also active.
- SSH banner reported 14 upgradable packages, 12 standard security updates. Applying upgrades was **not** part of this lab; follow-up pending.

## D3-06, D3-07 and visual confirmation

```bash
~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m py_compile ~/dragonstorm-lab/annotate_triton_detection.py
sudo systemctl is-active docker
sudo docker start triton-cpu   # only if stopped; use docker inspect first
curl -fsS http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready
~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/annotate_triton_detection.py
```

- Docker **active**; container resumed as `triton-cpu`; model **READY**; HTTP **200**.
- Input dog JPEG: 1546×1213 RGB; externally resized 300×300 UINT8 NHWC, 270,000 bytes, min 1 max 255.
- Triton inference: HTTP 200; `detection_boxes` [1,100,4], `detection_classes` [1,100], `detection_scores` [1,100], `num_detections` [1].
- Single dog detection, COCO ID **18**, score **0.969433**. Normalized box TLBR [0.0286422968, 0.1019492447, 0.9261913300, 0.9397560358]; original-image pixel LTRB **[158,35,1453,1123]**.
- Saved `/home/azureuser/dragonstorm-lab/test-dog-annotated.jpg`; output `ANNOTATION SMOKE TEST PASSED`. PowerShell initial multiline `scp` ordering failed; corrected single-line `scp -i <private-key-path> azureuser@<VM-public-IP>:/home/azureuser/dragonstorm-lab/test-dog-annotated.jpg <local-target>` completed (512 KB reported).
- Visual inspection: dog mostly enclosed; red rectangle and label render, some background included. **Not** ground-truth accuracy or calibrated probability.

## D4-02 — ONNX model/schema/internal-graph checks

On VM use `~/dragonstorm-lab/.venv-onnx-inspect/bin/python` and `onnx.load(..., load_external_data=False)` against `~/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx`.

1. Export producer `tf2onnx` **1.9.1**, graph IR **7**, opset **12**; input `inputs` **UINT8** symbolic [N,H,W,3], outputs four FLOAT detection arrays.
2. Initial graph nodes: **Cast** (to float), **Loop** in preprocessing, then **Mul/Sub**. Recursive inspection of GRAPH/GRAPHS attributes found `Resize__142` at **MAIN/Loop[7] node 12**.
3. Resize attributes: `mode=b'linear'`, `coordinate_transformation_mode=b'asymmetric'`, `exclude_outside=0`, `nearest_mode=b'floor'`. Inputs: `Transpose__5491:0`, `roi__129`, `const_empty_float__132`, `Concat__141:0`.
4. Loop path: Gather → Transpose → Shape → Gather → Slice → Concat → Resize; `Concat__141:0` takes `Slice__139:0` and `const_fold_opt__6007`. Initializer `Preprocessor/map/while/ResizeImage/stack:0=[300,300,3]` strongly indicates a 300×300 internal target, but full dimension-constant provenance not explicitly printed.
5. Normalize initializer `Preprocessor/mul/x:0 = 0.007843138`; subtraction `const_fold_opt__6209 = [[[[1.]]]]`. Therefore `pixel * 0.007843138 - 1` (approximately `pixel / 127.5 - 1`) is already in the graph. **Do not normalize UINT8 input externally.**
6. Live Triton `GET /v2/models/ssd_mobilenet_v1_12/config`: input UINT8 [-1,-1,-1,3]; `max_batch_size=0`; single `KIND_CPU` instance; four FP32 outputs. VM `free -h`: **15 GiB total, 14 GiB available, no swap**; readiness HTTP 200.
7. Tested optional libraries: `cv2` **NOT INSTALLED**, `scipy` **NOT INSTALLED**; NumPy + Pillow sufficient.

These inspections are reproduced by `scripts/inspect_onnx_preprocessing.py`.

## D4-03 — original-resolution inference

`python -m py_compile ~/dragonstorm-lab/original_resolution_inference.py` → **SCRIPT SYNTAX: PASSED**. Script loaded the unresized 1546×1213 image, `[1,1213,1546,3]` UINT8, **5,625,894 input bytes**; called existing `real_photo_triton_inference.infer/summarize`:

- HTTP **200**, all four expected FP32 output tensors, reported **2** detections.
- Slot 0: **cat, class 17**, score **0.804712**; slot 1: **dog, class 18**, score **0.505451**; identical normalized box [0.0181429982, 0.1113159060, 0.9376308918, 0.9294715524].
- One client-measured elapsed sample **0.073 s**. No claim that this is server-only or stable latency.
- Script is now version-controlled under `scripts/original_resolution_inference.py`.

## D4-04 — controlled resizing comparison

`scripts/compare_preprocessing.py` implements three paths:

- **A** unmodified 1546×1213 RGB → ONNX internal preprocessing: cat **0.804712**, dog **0.505451**, two detection slots.
- **B** Pillow BILINEAR 300×300 RGB (external): dog **0.969433**, one reported detection.
- **C** NumPy external asymmetric-coordinate bilinear 300×300, rounded to UINT8: cat **0.805172**, dog **0.511881**, two detections. A/C box coordinates nearly match.
- Pixel differences between B and C in-memory UINT8 arrays: mean absolute channel difference **6.087125925925926**, maximum **124**, **244939 of 270000** channel values differ (~90.72%).
- Single-request elapsed observations A **0.0436 s**, B **0.0293 s**, C **0.0280 s**. These are not benchmark aggregates.
- `python -m py_compile` passed for comparison script; runtime printed `D4-05 COMPARISON COMPLETE`. Images saved `d4-05-pillow-300.jpg` and `d4-05-asymmetric-300.jpg`, VM-local. Pillow inspection verified both RGB 300×300, respective sizes **15,993** and **19,919** bytes. JPEG files are **inspection artifacts**; inference consumed in-memory pixels, avoiding JPEG recompression.
- **Inference:** Strong evidence that resizing/sampling differences explain much of the cat-versus-dog discrepancy; not proof of exact equivalence because ONNX resizes floats and C rounds to UINT8. Higher confidence in one sample does not establish better overall accuracy.

## D4-06/07 — CPU baseline and concurrency benchmarking (November 13)

Script `scripts/benchmark_triton.py` uses Python `http.client` Triton V2 binary protocol, verifies HTTP 200, four response tensor names and binary payload sizes, and records client-observed request times. **Five warm-up calls** before each configuration; **30** timed sequential requests per input; **24** timed requests each for concurrency 1,2,4 (300×300 only). Loopback traffic, one Triton ONNX Runtime CPU instance; no GPU or Triton dynamic batching. Actual VM returned `BENCHMARK SYNTAX: PASSED` and `D4 TRITON BENCHMARK COMPLETE`.

| Workload | Requests | Mean ms | p50 ms | p95 ms | p99 ms | Min ms | Max ms | Throughput RPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 300×300 sequential | 30 | 27.903 | 27.624 | 30.251 | 31.144 | 26.883 | 31.391 | 35.49 |
| 1546×1213 sequential | 30 | 44.025 | 43.938 | 45.976 | 46.201 | 41.936 | 46.278 | 22.19 |
| 300×300 clients=1 | 24 | 27.473 | 27.744 | 27.984 | 28.039 | 26.732 | 28.052 | 35.95 |
| 300×300 clients=2 | 24 | 52.682 | 53.717 | 55.756 | 58.310 | 28.930 | 59.069 | 36.90 |
| 300×300 clients=4 | 24 | 100.722 | 106.804 | 109.736 | 109.776 | 31.060 | 109.787 | 36.85 |

Saved measured JSON on VM: `~/dragonstorm-lab/d4-triton-benchmark-results.json`. Repository includes a *transcription of the user-supplied output* in `docs/experiments/2026-11-13-cpu-baseline.json`; original VM JSON file has not been directly retrieved or byte-compared.

**Interpretation:** observed throughput plateaus around 36–37 RPS; more concurrency increases client response times rather than significantly improving throughput. 1546×1213 mean request time is about 58% higher than 300×300. With 24–30 samples, percentiles (especially p99) are exploratory. Queue bottleneck is *hypothesis* pending Triton server statistics and CPU utilization, not proven. The benchmark measures HTTP client wall time including local transfer, not isolated ONNX execution.

## Follow-up and cost controls

- **November 13 final shutdown verified:** User supplied a PowerShell screenshot showing `exit`, `logout`, closed SSH connection and return to local `PS` prompt, plus a separate Azure Portal VM Overview screenshot showing **Stopped (deallocated)**. This confirms deallocation at the captured end-of-session checkpoint, rather than merely SSH logout. Managed disks and applicable networking resources may still incur charges.
- Metrics endpoint was disabled in initial deployment; plan safe local-only Triton metrics/trace exposure and server-side queue/inference profiling as a separate experiment.
- Check NSG source IP on every new home-ISP lease; never open SSH/inference broadly.
- Recheck/upkeep the Ubuntu security updates in a separate controlled maintenance window.
- Next: server-side statistics, multiple model instances under controlled configuration, longer benchmarks and multi-image labeled quality evaluation; dynamic batching requires explicit future compatibility research/changes.

## End-of-session artifact and shutdown evidence — November 13

- The final shared terminal log also shows that the local benchmark journal was written and `ls -lh` verified three VM-local artifacts: `benchmark_triton.py` (~6.1 KiB), `d4-triton-benchmark-results.json` (~1.4 KiB), and `docs/journal/2026-11-13-triton-benchmark.md` (~1.8 KiB). Shell printed `BENCHMARK DOCUMENTATION: COMPLETE`. These are filesystem existence checks, **not** a claim that the VM-generated files were pushed directly from the VM.
- Repository scripts, technical journal and measured JSON transcription were separately committed via GitHub. The original VM JSON is still not byte-compared against the repository transcription.
- Windows PowerShell screenshot: session ended with `exit`, `logout`, `Connection ... closed.`, and local `PS` prompt; this verifies clean SSH disconnect.
- Azure Portal Overview screenshot: VM `vm-dragonstorm-ml-01` **Status: Stopped (deallocated)**; Azure compute deallocation at session end is **verified**. The screenshot does not establish zero ongoing storage/network costs or auto-shutdown configuration.
- Next boot: check current source IP against the SSH NSG rule and restart/check Triton readiness. Do not assume the Azure VM is currently running.

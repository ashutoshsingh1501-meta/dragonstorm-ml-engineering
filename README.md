# Operation Dragon Storm — ML Engineering

**From ML fundamentals to production AI systems — one verified experiment at a time.**

A public, hands-on engineering and learning journal covering the lifecycle of AI systems: data preparation, model development, evaluation, model packaging, deployment, inference optimization, monitoring, and production trade-offs.

This is an **independent, greenfield lab** running on a personally owned Microsoft Azure subscription. It uses original project material, open-source tools, and public or synthetic data; it is not a reconstruction of any employer's proprietary systems.

> **Latest verified checkpoint — November 13, 2026:** Real-image Triton CPU inference and annotated dog JPEG validated; ONNX-internal asymmetric resizing and pixel normalization investigated; A/B/C preprocessing experiment completed; first sequential and concurrency CPU benchmark completed. **300×300 baseline:** p50 **27.624 ms**, p95 **30.251 ms**, throughput **35.49 RPS** (30 requests). At 1/2/4 concurrent clients throughput ~**35.95/36.90/36.85 RPS** while mean latency rose ~**27.5/52.7/100.7 ms**. Exploratory local-only measurements, not production benchmarks. Azure VM **final Nov 13 deallocation not verified**. See [tracker](docs/PROGRESS.md), [journal](docs/journal/2026-11-13-triton-preprocessing-benchmark.md), [benchmark results](docs/experiments/2026-11-13-cpu-baseline.json).

## Current lab architecture

```text
Personal Windows workstation
  └── SSH (restricted Azure NSG rule) / Azure Portal
       └── Personal Azure VM: vm-dragonstorm-ml-01
            Central India · Ubuntu Server 24.04 LTS
            Standard D4as v5 · 4 vCPUs · 16 GiB RAM
            128-GiB provisioned OS disk (~123 GiB filesystem)
            │
            ├── Docker Engine 29.9.3 (containerd 2.4.2)
            ├── Isolated Python 3.12 environment for ONNX inspection
            │
            └── Triton Inference Server 2.74.0 (Docker)
                 Image: nvcr.io/nvidia/tritonserver:26.10-py3
                 HTTP: 127.0.0.1:8000 on VM host only
                 GPU: none; CPU execution instance
                 Model repository: /models (read-only bind mount)
                   └── ssd_mobilenet_v1_12/
                        ├── config.pbtxt
                        └── 1/model.onnx  (binary on VM; not in GitHub)
```

**Cost-control state at Day 1 close:** Azure Portal confirmed `Stopped (deallocated)`. Compute billing stops while the VM is deallocated; managed disks and applicable networking resources may still incur charges. Auto-shutdown was temporarily set to **Off** during setup; restoring an automatic shutdown schedule is a future safeguard.

## Day 1 — verified results (2026-11-04)

| Checkpoint | Observed outcome |
| --- | --- |
| Ubuntu environment | Ubuntu 24.04 LTS; 4 vCPUs; ~15 GiB usable RAM; OS packages updated |
| Docker | CE client/server **29.9.3**; `hello-world` completed |
| Triton image | `nvcr.io/nvidia/tritonserver:26.10-py3` pulled; digest `sha256:b404f7de5dbeeefe0b17d7d149745a50d0989a25d0d831433b5ba63c716c2fcd` |
| Triton serving | **2.74.0**; HTTP bound to host loopback; gRPC and metrics disabled for the initial lab |
| Model provenance | Public ONNX Model Zoo SSD-MobileNetV1-12 artifact; local SHA-256 matched the recorded upstream digest |
| ONNX graph verification | Isolated `onnx==1.19.1`; graph IR 7, opset 12; `onnx.checker.check_model` **PASSED** |
| Triton configuration | Explicit I/O names, `backend: "onnxruntime"`, one `KIND_CPU` instance, `max_batch_size: 0` |
| Model load | Logs: `successfully loaded 'ssd_mobilenet_v1_12'`; version **1**, status **READY** |
| Model-specific readiness | `GET /v2/models/ssd_mobilenet_v1_12/ready` → **HTTP 200 OK** |
| End-of-day Azure state | Portal verified VM **Stopped (deallocated)** |

**Evidence boundary:** The `READY` and HTTP 200 observations establish that Triton loaded and reported the model as ready. They do **not** establish successful image prediction, accuracy, latency, throughput, or production suitability. CUDA driver/helper and virtual-device discovery warnings appeared on the CPU-only host, but did not prevent the CPU model from loading.

### First ONNX model contract (verified from the actual artifact)

Model: `ssd_mobilenet_v1_12`, version `1`, ONNX opset `12`.

| Direction | Tensor | Type | Dimensions |
| --- | --- | --- | --- |
| Input | `inputs` | UINT8 | `[-1, -1, -1, 3]` (rank-4, channels-last) |
| Output | `detection_boxes` | FP32 | `[-1, -1, 4]` |
| Output | `detection_classes` | FP32 | `[-1, -1]` |
| Output | `detection_scores` | FP32 | `[-1, -1]` |
| Output | `num_detections` | FP32 | `[-1]` |

Symbolic ONNX dimensions are represented as `-1` in the initial Triton configuration; no cross-output dimension equalities were experimentally verified. With `max_batch_size: 0`, the model's leading dimension remains part of the explicit tensor shape, and **Triton dynamic batching is not enabled**.

- [Source research, model hash, graph metadata and load evidence](docs/models/ssd-mobilenetv1-12-source-notes.md)
- [Version-controlled Triton `config.pbtxt`](model_repository/ssd_mobilenet_v1_12/config.pbtxt)

The model binary is downloaded to the lab VM, not committed to this public repository. Review third-party model licenses and usage terms before redistribution.

## Roadmap

See the full [phase/milestone tracker](docs/PROGRESS.md). Each phase has a testable evidence boundary.

| Phase | Outcome | Status as of Nov 13 |
| --- | --- | --- |
| 00 Lab foundation | Personal Azure, safe SSH, Docker, cost discipline | VM/Docker/SSH working; auto-shutdown setup and Nov 13 final deallocation **unverified** |
| 01 First vision inference | Real detection output + visualization | **Functional smoke test complete**, single dog photo annotated |
| 02 Model evaluation | Multi-image labels, IoU, precision/recall/mAP and failure analysis | **Not started** |
| 03 Model training | Train or tune a model, tracked experiment | **Not started** |
| 04 Packaging & contracts | Model provenance, ONNX and preprocessing interpretation | **Partial**: artifact/graph checked; internal normalization and resize traced; no end-to-end export workflow |
| 05 Triton serving | ONNX Runtime CPU model, V2 HTTP, output decoding | **Functional baseline complete** |
| 06 Performance engineering | Warmed client latency percentiles, throughput and concurrency | **First exploratory CPU benchmark complete**; longer and server-side measurement pending |
| 07 Batching and scaling | Compare instance count, batching and resource use | **Not started**; config currently max_batch_size=0 |
| 08 Applied CV pipeline | Detection→crop→embedding→retrieval | Not started |
| 09 Production hardening | Metrics, security, IaC, CI, rollback | Not started |

## Next session — server-side profiling & evaluation

1. Confirm safe VM startup, effective current-client-IP SSH NSG, Docker and model readiness.
2. Capture Triton model inference statistics/queue-versus-compute timing and CPU utilization; initial Triton metrics were disabled, so configuration changes require a distinct controlled experiment.
3. Compare one versus multiple CPU model instances without overwriting the measured single-instance configuration or claiming dynamic batching.
4. Repeat larger-sample benchmarks with controlled warm-ups/traffic; only compare like-for-like request sizes and methodology.
5. Collect labeled test images to validate class quality and boxes; a correct result on one dog photo does not establish model accuracy.
6. Deallocate Azure VM after use and **verify** the Azure power state.

**Working rule:** Preserve real terminal outputs, note failures as well as passes, keep public repository free of private keys/account IDs/private IPs, and clearly label hypotheses.

## Why this project?

A useful ML model is only one part of a reliable AI product. The purpose of this project is to develop practical judgment about the decisions required to move from an idea to a reproducible, observable and deployable system.

Each experiment should answer:

1. **What problem are we solving?**
2. **What did we build, and how can someone reproduce it?**
3. **What did we measure, and against which baseline?**
4. **What failed or surprised us?**
5. **What trade-offs emerged, and what should we test next?**

## Learning tracks

| Track | Topics |
| --- | --- |
| Data engineering | Ingestion, quality, versioning, transformations, batch vs. streaming |
| ML foundations | Problem framing, splitting, leakage, features, baselines, bias/variance |
| Model development | Training, fine-tuning, experiments and reproducibility |
| Evaluation | Precision/recall, mAP, error analysis, latency and cost |
| Computer vision | Classification, detection, cropping, embeddings, retrieval |
| MLOps | Model artifacts, versioning, ONNX, containers, CI/CD |
| Model serving | Triton, model repositories, HTTP/gRPC, concurrency and batching |
| Production engineering | Load testing, observability, reliability, scaling and security |
| Applied AI (later) | Vector search, RAG and agent workflows where relevant |

## Engineering evidence and reproducibility

The authoritative records are the **verified milestone tracker** and **chronological engineering journal**, including failures, corrective actions, exact commands and observed results. [Nov 12–13 preprocessing and CPU benchmark journal](docs/journal/2026-11-13-triton-preprocessing-benchmark.md) and [terminal-transcribed JSON](docs/experiments/2026-11-13-cpu-baseline.json) are the latest records.

- [Progress tracker](docs/PROGRESS.md)
- [Operations, SSH recovery, reproducible commands and cost controls](docs/OPERATIONS.md)
- [Day 1: Azure, Docker, Triton and ONNX bootstrap journal](docs/journal/2026-11-04-azure-bootstrap.md)
- [Day 2: First inference client and real-photo test](docs/journal/2026-11-06-day-2.md)
- [Day 3: COCO class mapping and annotation setup](docs/journal/2026-11-07-day-3.md)
- [Nov 12–13: Preprocessing, annotation and CPU benchmarks](docs/journal/2026-11-13-triton-preprocessing-benchmark.md)
- [ADR-001: Personal Azure cloud-first decision](docs/decisions/ADR-001-personal-azure-cloud-first.md)
- [SSD-MobileNetV1-12 source and verification notes](docs/models/ssd-mobilenetv1-12-source-notes.md)

Experiment records distinguish **observations**, **inferences**, and **hypotheses**. Performance measurements will include hardware, inputs, units, baselines and uncertainty. CPU-only results will not be presented as representative GPU production benchmarks.

### Repository layout (implemented)

```text
README.md
docs/
  PROGRESS.md
  OPERATIONS.md
  decisions/ADR-001-personal-azure-cloud-first.md
  journal/
    2026-11-04-azure-bootstrap.md
    2026-11-06-day-2.md
    2026-11-07-day-3.md
    2026-11-13-triton-preprocessing-benchmark.md
  models/ssd-mobilenetv1-12-source-notes.md
  experiments/2026-11-13-cpu-baseline.json
model_repository/ssd_mobilenet_v1_12/config.pbtxt
scripts/
  first_triton_inference.py
  real_photo_triton_inference.py
  annotate_triton_detection.py
  original_resolution_inference.py
  compare_preprocessing.py
  inspect_onnx_preprocessing.py
  benchmark_triton.py
  check_triton_lab.sh
  diagnose_ssh_guest.sh
```

**Artifacts kept on VM, not GitHub:** downloaded third-party ONNX model binary, test JPEG, annotated output JPEG, COCO label map, local virtualenv, original benchmark JSON and experimental visual JPG outputs. Repository JSON is explicitly a transcription from terminal stdout.

## Reproducing the verified experiment

On an authorized Azure VM session with Docker and the locally provisioned model ready:

```bash
curl -fsS http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready
~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/annotate_triton_detection.py
~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/original_resolution_inference.py
~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/compare_preprocessing.py
~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/benchmark_triton.py
```

Copy the version-controlled scripts into `~/dragonstorm-lab/` on the VM, so imports of `real_photo_triton_inference.py` work. A full environment installer and CI tests are not yet provided. For checked commands, interpretation, A/B/C observations, and caveats see the [Nov 12–13 journal](docs/journal/2026-11-13-triton-preprocessing-benchmark.md).

## Publication and responsible use

- Keep this project separate from employer/client infrastructure, confidential data, and proprietary code.
- Do **not** commit secrets, SSH private keys, personal subscription IDs, VM IP addresses, raw terminal transcripts containing private details, or unredacted Azure Portal screenshots.
- Use original code and appropriately licensed public or synthetic materials; review licenses for every third-party model, dataset and dependency.
- The repository's MIT license covers original project code, **not** third-party models or datasets.
- Publish truthful outcomes, including failed attempts, performance limitations and incomplete milestones.

## Sharing the journey

This lab provides a foundation for engineering write-ups on model provenance, reproducibility, CPU vs. GPU trade-offs, inference-serving choices, batching and performance measurements — once those experiments have been performed.

**Maintainer:** Ashutosh Singh  
**Status:** First functional Triton detection + annotation and exploratory CPU benchmarks completed (as of 2026-11-13)  
**License:** MIT for original repository content; third-party assets retain their own terms.

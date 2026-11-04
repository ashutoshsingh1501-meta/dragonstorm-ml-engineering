# Operation Dragon Storm — ML Engineering

**From ML fundamentals to production AI systems — one verified experiment at a time.**

A public, hands-on engineering and learning journal covering the lifecycle of AI systems: data preparation, model development, evaluation, model packaging, deployment, inference optimization, monitoring, and production trade-offs.

This is an **independent, greenfield lab** running on a personally owned Microsoft Azure subscription. It uses original project material, open-source tools, and public or synthetic data; it is not a reconstruction of any employer's proprietary systems.

> **Latest verified checkpoint — Day 1, November 4, 2026:** Docker Engine installed; NVIDIA Triton 2.74.0 running in a CPU-only container; an SSD-MobileNetV1-12 ONNX model validated and successfully loaded by Triton's ONNX Runtime backend; **model-specific HTTP readiness returned 200 OK**. The Azure VM was **Stopped (deallocated)** at the end of the session. **Actual image inference, prediction quality, and performance benchmarks are not yet tested.**

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

The roadmap tracks **observable outcomes**, not only tools installed. Work can overlap phases, but incomplete inference or evaluations are never marked complete.

| Phase | Target outcome | Status after Day 1 |
| --- | --- | --- |
| 00 — Lab foundation | Personal Azure, secure access, cost controls, VM/Docker setup | **Initial bootstrap complete**; auto-shutdown restoration pending |
| 01 — First vision inference | Run a public vision model and inspect real prediction outputs | **In progress**; ONNX model deployed and ready, inference pending |
| 02 — Model evaluation | Public/synthetic examples, baseline quality, failure analysis | Not started |
| 03 — Model training | Train or fine-tune a small model; track experiments | Not started |
| 04 — Model packaging | ONNX validation; preprocessing/postprocessing contract and export workflow | **Partially started**; imported ONNX graph validated, remaining work pending |
| 05 — Triton serving | CPU model load, HTTP readiness, and actual end-to-end inference | **In progress**; load/readiness passed, inference pending |
| 06 — Performance engineering | p50/p95/p99 latency, throughput and errors at varying concurrency | Not started |
| 07 — Batching and scaling | Batching on/off, utilization and scaling decisions | Not started |
| 08 — Applied CV pipeline | Detection → crops → embeddings → vector similarity | Not started |
| 09 — Production hardening | CI/CD, observability, security, versioning, recovery/rollback | Not started |

## Next session — Day 2

**Resume at the first real CPU inference test.** The VM was deallocated at the end of Day 1. After starting it again, reconnect via SSH, inspect/resume the retained `triton-cpu` Docker container, and recheck model readiness before sending an inference request.

1. Construct a controlled image tensor following the verified **UINT8 NHWC** model input schema and confirm any required preprocessing.
2. Send a request to Triton's localhost **V2 inference** endpoint.
3. Inspect the four returned detection tensors and validate their shapes and values.
4. Only after observing actual predictions, decode class labels and render bounding boxes.
5. Defer batching, load testing, GPU comparisons and benchmarks until a reproducible baseline exists.

**Working rule:** One command or configuration action → review the user's actual output → document and commit the verified result → proceed to the next action. Never label an untested hypothesis as a result.

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

The authoritative records are the **verified milestone tracker** and **chronological engineering journal**, including failures, corrective actions, exact commands and observed results.

- [Progress tracker](docs/PROGRESS.md)
- [Day 1: Azure, Docker, Triton and ONNX bootstrap journal](docs/journal/2026-11-04-azure-bootstrap.md)
- [ADR-001: Personal Azure cloud-first decision](docs/decisions/ADR-001-personal-azure-cloud-first.md)
- [SSD-MobileNetV1-12 source and verification notes](docs/models/ssd-mobilenetv1-12-source-notes.md)

Experiment records distinguish **observations**, **inferences**, and **hypotheses**. Performance measurements will include hardware, inputs, units, baselines and uncertainty. CPU-only results will not be presented as representative GPU production benchmarks.

### Repository layout (implemented and planned)

```text
README.md
docs/
  PROGRESS.md                               # Verified milestone tracker
  decisions/
    ADR-001-personal-azure-cloud-first.md
  journal/
    2026-11-04-azure-bootstrap.md           # Day 1 command/output journal
  models/
    ssd-mobilenetv1-12-source-notes.md      # Model research and evidence
model_repository/
  ssd_mobilenet_v1_12/
    config.pbtxt                            # Triton config only (no model weights)

# To be added when backed by real experiments:
src/                                        # Original inference/pipeline code
scripts/                                    # Repeatable setup and test commands
tests/                                      # Functional/integration/evaluation tests
docs/experiments/                           # Results and methods
```

## Publication and responsible use

- Keep this project separate from employer/client infrastructure, confidential data, and proprietary code.
- Do **not** commit secrets, SSH private keys, personal subscription IDs, VM IP addresses, raw terminal transcripts containing private details, or unredacted Azure Portal screenshots.
- Use original code and appropriately licensed public or synthetic materials; review licenses for every third-party model, dataset and dependency.
- The repository's MIT license covers original project code, **not** third-party models or datasets.
- Publish truthful outcomes, including failed attempts, performance limitations and incomplete milestones.

## Sharing the journey

This lab provides a foundation for engineering write-ups on model provenance, reproducibility, CPU vs. GPU trade-offs, inference-serving choices, batching and performance measurements — once those experiments have been performed.

**Maintainer:** Ashutosh Singh  
**Status:** Day 1 bootstrap complete; first real inference pending (as of 2026-11-04)  
**License:** MIT for original repository content; third-party assets retain their own terms.

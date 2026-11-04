# Operation Dragon Storm — ML Engineering

**From ML fundamentals to production AI systems.**

A public, hands-on learning and engineering journal exploring the complete lifecycle of AI systems: data preparation, model development, evaluation, deployment, inference optimization, monitoring, and production trade-offs.

This repository is **an independent greenfield lab**. It uses original code, open-source tooling, and public or synthetic data. It is not a reconstruction of any employer's proprietary systems.

> **Current stage (2026-11-04):** Personal Azure Ubuntu VM deployed; restricted SSH connectivity verified; CPU/RAM/storage checked; Ubuntu security and maintenance updates applied. Docker Engine, NVIDIA Triton, model inference, and performance benchmarks have **not yet** been completed.

## Why this project?

Understanding an ML model is only one part of building a reliable AI product. This project studies the decisions and measurements needed to move from an idea to a reproducible, observable, deployable service.

Each experiment should answer:
1. **What problem are we solving?**
2. **What did we build, and how can someone reproduce it?**
3. **What did we measure, against which baseline?**
4. **What failed or surprised us?**
5. **What are the trade-offs and the next hypothesis?**

## Learning tracks

| Track | Topics |
| --- | --- |
| Data engineering | Data ingestion, quality, versioning, transformations, batch vs. streaming |
| ML foundations | Problem framing, splits, leakage, features, baselines, bias/variance |
| Model development | Training, fine-tuning, reproducibility, hyperparameters, experiment tracking |
| Evaluation | Precision/recall, mAP, confusion matrices, error analysis, latency and cost |
| Computer vision | Image classification, object detection, cropping, embeddings and retrieval |
| MLOps | Artifacts, model registry, ONNX export, containers, CI/CD, reproducible pipelines |
| Model serving | NVIDIA Triton, model repositories, HTTP/gRPC, concurrency, dynamic batching |
| Production engineering | Load tests, observability, scaling, rollbacks, reliability and security |
| Applied AI (later) | Retrieval systems, vector search, RAG and agent workflows where relevant |

## Roadmap

This is a **living sequence**, not a claim that every track is already implemented. We may reorder phases based on available hardware and validated dependencies.

| Phase | Planned outcome | Status |
| --- | --- | --- |
| 00 — Lab foundation | Personal Azure tenant/subscription, spending safeguards, Git workflow, secure remote development | In progress |
| 01 — First vision inference | Run an openly licensed vision model and inspect correct outputs | Not started |
| 02 — Model evaluation | Public/synthetic evaluation samples, baseline quality metrics and failure cases | Not started |
| 03 — Model training | Train or fine-tune a small vision model, track experiments and compare to baseline | Not started |
| 04 — Model packaging | Export and validate ONNX; define preprocessing/postprocessing contract | Not started |
| 05 — Triton serving | Serve supported model via Triton, validate end-to-end inference | Not started |
| 06 — Performance engineering | Measure p50/p95/p99 latency, throughput and errors under varying concurrency | Not started |
| 07 — Batching and scaling | Compare batching off/on, resource utilization, deployment trade-offs | Not started |
| 08 — Applied CV pipeline | Detection → crops → embeddings → vector similarity search | Not started |
| 09 — Production hardening | Testing, CI/CD, observability, versioning, and deployment/rollback design | Not started |

### First practical milestone

**Establish a separately owned personal Azure subscription** (not linked to an employer tenant), verify billing and region/compute quotas, then select cloud compute and storage for the first vision experiment. The personal laptop is a management client only; training and model serving will run on Azure. Confirm running costs and safeguards before creating paid resources.

## Verified hands-on progress

Documentation is updated **after each verified action or small reproducible checkpoint**, never before execution. Failures and resolved blockers are first-class learning outcomes.

- [Live milestone tracker](docs/PROGRESS.md)
- [2026-11-04 Azure VM and Ubuntu bootstrap journal](docs/journal/2026-11-04-azure-bootstrap.md)
- [ADR-001: Personal Azure cloud-first lab architecture](docs/decisions/ADR-001-personal-azure-cloud-first.md)

Next proposed action: install Docker repository prerequisites; it is **pending**, not completed.

## Experiment documentation standard

Every meaningful experiment will record:
- **Question and hypothesis** — what change are we testing?
- **Environment** — OS, CPU/GPU, RAM, versions, model, input sizes, hardware constraints.
- **Dataset/model provenance** — source, version, license, preprocessing, limitations.
- **Method** — runnable commands, configuration, workload, repetitions and controls.
- **Results** — measured numbers, units, baselines, raw outputs or reproducible summaries.
- **Interpretation** — bottlenecks, uncertainty, confounders and failure analysis.
- **Decision and next step** — what to keep, change or test next.

We will explicitly distinguish **observations**, **inferences**, and **hypotheses**. Benchmarks from CPU-only experiments will not be presented as representative of GPU production workloads.

## Planned repository layout

As milestones begin, code and documentation will be added incrementally:

```text
docs/
  roadmap/              # Detailed milestones and learning notes
  decisions/            # Architecture decision records (ADRs)
  experiments/          # Reproducible experiment journals and results
  diagrams/             # Architecture and pipeline diagrams
src/                    # Original application and pipeline code
models/                 # Lightweight model configuration; not large weights
scripts/                # Repeatable setup, validation and load-test scripts
tests/                  # Unit, integration and evaluation tests
```

Some documentation directories now exist (for example `docs/journal` and `docs/decisions`); source, model, test and script directories will be added incrementally as real experiments begin.

## Publication and responsible use

- Use an independently owned personal Azure account and independently sourced public or synthetic material. The personal laptop is only used for browser, SSH, Git and remote development; ML compute is provisioned in Azure.
- Do **not** commit customer or employer datasets, code, credentials, screenshots containing secrets, or confidential architecture.
- Review the licenses and usage terms of every model, dataset and dependency before including or redistributing artifacts.
- The repository's MIT license applies to original project code; it does not relicense third-party models or datasets.
- Publish honest outcomes, including blocked attempts, limitations, failed experiments and negative results.

## Sharing the journey

Over time, this repo will support technical posts about engineering decisions: model-selection trade-offs, reproducible evaluation, container constraints, serving architecture, batching behavior, and latency/throughput measurements.

**Maintainer:** Ashutosh Singh  
**Status:** Learning in public — setup phase  
**License:** MIT for original repository content; third-party assets retain their own terms.

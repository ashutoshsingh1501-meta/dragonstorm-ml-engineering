# ADR-001 — Personal Azure Cloud-First ML Engineering Lab

- **Status:** Accepted for initial experimentation
- **Decision date:** 2026-11-04
- **Scope:** Operation Dragon Storm learning environment, not a production architecture

## Context

The goal is to study the complete ML engineering lifecycle: data, training, evaluation, packaging, deployment, performance, observability, and later GPU-serving patterns.

A personal laptop is used for browser, SSH, Git and remote development, **not for hosting the ML workloads**. A prior corporate-environment experiment encountered virtualization, cloud account and capacity restrictions; separating the lab from company infrastructure avoids ownership and compliance ambiguity.

The initial cloud lab must provide an actual, reproducible **CPU inference baseline** without implying it is representative of GPU production throughput.

## Decision

1. Use a **personally owned Azure subscription** and an independent, open-source/synthetic-data project.
2. Begin with a single **Standard_D4as_v5** Ubuntu 24.04 x64 VM in **Central India** (4 vCPUs / 16 GiB RAM).
3. Use a 128 GiB Premium SSD OS disk initially; validate observed disk headroom before any large image download.
4. Use SSH public-key authentication; expose port 22 only to the currently authorized public client IP via NSG; do not publicly expose inference ports.
5. Configure daily auto-shutdown for **20:00 IST**, with notification. Check for `Stopped (deallocated)` after stopping compute.
6. Avoid B-series burstable CPU VMs as the first sustained-load benchmark platform to reduce CPU-credit confounding.
7. Document exact image/backend, open-source model license, measurements and reproducible setup before publishing benchmark conclusions.
8. Treat GPU migration as a separate decision, subject to quotas, availability, compatibility, and an approved cost estimate.

## Alternatives considered

| Alternative | Why not the primary starting point |
| --- | --- |
| Local personal laptop | Hardware constraints would dominate model/runtime selection; conflicts with the cloud-first learning objective |
| Company laptop or corporate Azure | Independent personal experimentation should not depend on corporate approvals, tenant policy or assets |
| GitHub Codespaces | Previous large Triton image attempt exhausted practical environment resources; not preferred as the serving host |
| Azure B-series burstable | CPU-credit behavior can complicate sustained-load benchmark comparisons |
| GPU Azure VM immediately | Regional vCPU limit and GPU SKU/quota availability need separate verification |
| Managed inference service immediately | Obscures initial model-server, Linux and container-level fundamentals we want to learn |

## Consequences and risks

- Compute is billed while allocated/running; disk and some other resources can accrue charges even when VM is deallocated.
- Free credits, subscriptions quotas and per-SKU capacity are distinct constraints.
- A single VM is **not** highly available; its design is appropriate for a learning lab only.
- CPU inference measurements are useful for reproducible concurrency analysis, not as GPU production performance predictions.
- A home public IP can change and require NSG source update.
- An accepted but independently unverified SSH host key fingerprint remains a security follow-up.
- The current design does not provide automated infrastructure-as-code deployment. A reproducible IaC baseline may be added later.

## Verification status

- Azure deployment and SSH connection: **Verified**.
- Ubuntu OS/CPU/RAM/disk inventories and security updates: **Verified**.
- Docker engine, Triton model server, GPU inference, model training and evaluation: **Not yet executed**.

## References

- [Engineering progress](../PROGRESS.md)
- [2026-11-04 lab journal](../journal/2026-11-04-azure-bootstrap.md)


## Implementation-status addendum — 2026-11-13

The original decision still stands. **Subsequent verification:** Docker Engine, Triton 2.74.0, ONNX CPU serving, localhost V2 inference, dog-image annotation, ONNX preprocessing trace and exploratory concurrency/latency benchmarking have all been executed. See [current tracker](../PROGRESS.md) and [Nov 12–13 journal](../journal/2026-11-13-triton-preprocessing-benchmark.md). GPU, dynamic batching, infrastructure-as-code, training, and production observability remain untested.

**Operational incident:** An ISP-assigned home public IP changed; the restricted Azure NSG SSH rule still referenced the old source, causing SSH refusal. The user updated the rule to **My IP Address** and confirmed a successful SSH login. SSH service/socket diagnostics were collected, but inactive socket-activated `ssh.service` was *not* independently proven to be the cause.

**Cost-control distinction:** The portal screenshot verified **Stopped (deallocated)** at the end of November 7, but no November 13 deallocation verification was supplied. Original ADR intended 20:00 IST auto-shutdown; setup had it temporarily turned off. Its eventual re-enablement is still pending evidence. SSH `exit` does not deallocate the Azure VM.

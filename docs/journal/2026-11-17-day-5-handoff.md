# Day 5 handoff — Triton server-side profiling (plan only)
**Prepared:** 2026-11-17  
**Execution state:** **NOT STARTED.** This is a handoff/next-session checklist, not evidence of a newly run experiment.  
**Last user-verified lab state:** 2026-11-13, Azure VM `vm-dragonstorm-ml-01` was **Stopped (deallocated)** after a clean SSH exit. No later guest-shell access or power state was provided.

## Purpose and Cat-Eye relevance

The independent DragonStorm ML Lab serves as a practical public-data reference for discussing NVIDIA Triton integration, ONNX Runtime model packaging, preprocessing contracts, inference API design, and capacity tuning. It is **not** Cat-Eye source code or verified Cat-Eye infrastructure. The next relevant learning goal is to **measure where request time is spent before changing CPU serving capacity**.

## Verified handoff baseline

| Aspect | Last verified state |
| --- | --- |
| Platform | Personal Azure Central India Ubuntu 24.04 VM; Standard D4as v5, 4 vCPU / 16 GiB |
| Serving | NVIDIA Triton 2.74.0 in Docker (`triton-cpu`), host-local HTTP port 8000 only |
| Backend | Triton ONNX Runtime; one CPU instance; `max_batch_size: 0` (no Triton dynamic batching) |
| ONNX model | `ssd_mobilenet_v1_12`, version `1`; local model weights on VM only, not in Git |
| Input contract | `UINT8` NHWC `[-1,-1,-1,3]`, channel count 3 |
| Output contract | `detection_boxes`, `detection_classes`, `detection_scores`, `num_detections`, all FP32 |
| Functionality | Real JPEG inference, COCO class 18 dog (96.9433% score on Pillow-resized image), annotated JPEG visually inspected |
| Original image | 1546×1213 RGB; **73 ms** one-time client sample, top reported cat 0.804712 and dog 0.505451 |
| Preprocessing | ONNX `Loop/Resize` linear/asymmetric; [300,300,3] constant; multiply by 0.007843138, subtract 1 |
| A/B/C | Original input: cat 0.804712; Pillow 300×300: dog 0.969433; NumPy asymmetric 300×300: cat 0.805172 |
| External-resize difference | Pillow vs NumPy asymmetric channel MAE **6.0871**; outputs depend materially on preprocessing |
| 300×300 sequential (30 calls) | Mean **27.903 ms**; p50 **27.624 ms**; p95 **30.251 ms**; p99 **31.144 ms**; throughput **35.49 RPS** |
| 1546×1213 sequential (30 calls) | Mean **44.025 ms**; p50 **43.938 ms**; p95 **45.976 ms**; throughput **22.19 RPS** |
| 300×300 clients 1/2/4 (24 calls each) | RPS **35.95 / 36.90 / 36.85**, mean latency **27.473 / 52.682 / 100.722 ms** |
| VM cost management | Portal screenshot confirmed **Stopped (deallocated)** Nov 13; auto-shutdown reenablement still unverified |

**Evidence interpretation:** HTTP 200 and a high score validate functional inference, not detector accuracy. The close A/C scores support a resize-sampling explanation, not identical underlying tensors. Throughput plateau suggests a bottleneck but queue saturation remains a *hypothesis*. Current measurements are client HTTP loopback timing with limited samples—not server-only Triton time, production SLAs or GPU results.

## Primary source artifacts

- [Detailed Nov 12–13 command journal](2026-11-13-triton-preprocessing-benchmark.md) — actual successes/failures, commands, terminal outputs, latency table and shutdown
- [Latest reconciled milestone tracker](../PROGRESS.md) — statuses and historical ledger
- [Benchmark stdout transcription](../experiments/2026-11-13-cpu-baseline.json) — **not** independently downloaded from VM
- [ONNX model evidence](../models/ssd-mobilenetv1-12-source-notes.md)
- [VM/SSH start-stop runbook](../OPERATIONS.md)
- [Git versioned Triton config](../../model_repository/ssd_mobilenet_v1_12/config.pbtxt)
- [Inference/annotation clients](../../scripts/)
- [Day 5 read-only statistics snapshot helper](../../scripts/d5_triton_stats_snapshot.sh) — created in repository but **not run on VM**

## Day 5 proposed sequence (all pending)

### D5-00 — Safe reconnection and no-change baseline
1. Start Azure VM via portal; confirm SSH NSG source allows the current home/public client IP only; do not expose Triton ports publicly.
2. SSH from Windows with locally stored private key. No private key or VM public IP should be committed.
3. Check `sudo systemctl is-active docker`. If `triton-cpu` is stopped, resume the existing container. Allow for warm-up readiness; `GET /v2/models/ssd_mobilenet_v1_12/ready` should return HTTP 200.
4. Check actual loaded config `GET /v2/models/ssd_mobilenet_v1_12/config`, single CPU instance / `max_batch_size: 0`. Preserve existing config and baseline results; do not change parameters before profiling.
5. Run the [read-only lab checker](../../scripts/check_triton_lab.sh) (copy the current repo script to VM first if needed).

### D5-01 — Read-only model statistics endpoint
The Triton V2 **Model Statistics** endpoint is distinct from the optional Prometheus `/metrics` endpoint. The initial server had Prometheus metrics disabled, but statistics may still be available; **verify** rather than assuming.

```bash
curl -fsS http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/stats \
  | ~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m json.tool
```

Capture baseline stats **before** the controlled workload. If the endpoint is disabled or returns an error, retain HTTP status/body and do not silently reconfigure serving. Use `scripts/d5_triton_stats_snapshot.sh` to write JSON snapshots.

### D5-02 — Pre/post-load stats and CPU observation
After warm-up, record stats-before, run the **same 300×300 input** using the existing benchmark (or a longer script once reviewed), record stats-after, and capture host CPU usage (`top`, `pidstat` if available, `docker stats`).
- Use **delta counters**, not raw cumulative counters, for queue/compute breakdowns.
- Record warmup count, request count, input shape, workers, elapsed wall time, median/p95, throughput and any errors.
- Check whether the API reports cumulative `inference_stats` durations (queue, compute_input, compute_infer, compute_output); be careful about counts and units, and don't presume one field always exists.
- Save raw VM results for comparison with stdout transcription. Server stats and concurrent client timings need not have identical scope.

### D5-03 — Only then controlled CPU-instance scaling
If queue and compute evidence warrant it, record the **existing `config.pbtxt` and container invocation**; test `instance_group.count=2` as a separate, reversible configuration. Avoid changes that break model load, port locality, or the working one-instance baseline. Recheck readiness. Compare the **same workload** for 1 vs 2 instances; do not assume a speedup because ONNX CPU intra-/inter-op threading may oversubscribe 4 vCPUs. GPU and dynamic batching remain **out of scope** until separate design decisions.

### D5-04 — Completion artifacts
Commit a dated executed journal **only after user-provided command output**, including: initial VM/NSG checks, stats endpoint result, before/after counters, CPU measurements, benchmark commands, comparison, failures/rollbacks, scripts and refreshed tracker. Explicitly mark observed vs inferred. Verify the actual Azure **Stopped (deallocated)** status after shutdown.

## Deferred quality and maintenance
- Evaluate multiple labeled images, box IoU, precision/recall/mAP and failure cases before making a preprocessing correctness claim; one dog photo is not a quality benchmark.
- Original ONNX resize target's dynamic `Concat` constant provenance is not exhaustively printed.
- The model binary, COCO map and example JPEG remain on VM; do not redistribute or commit them without license review.
- Ubuntu banner on Nov 12–13 showed 14 available updates, including 12 standard security updates; treat patching as a separate change window.
- Azure auto-shutdown restoration remains unverified; cloud compute incurs cost while allocated.

**Handoff decision (as of 2026-11-17):** **Begin D5-00 and D5-01 next.** No fresh benchmark, stats response or scaling result has been observed since 2026-11-13.

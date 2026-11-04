# First detection model candidate: SSD-MobileNetV1-12 (ONNX)

Status: **Source/model-card research completed; binary not yet downloaded, inspected, loaded or tested**.

## Why this candidate

The ONNX Model Zoo's SSD-MobileNetV1-12 is an actual object detection model trained against MS COCO 2017; it produces bounding boxes, scores, class IDs, and detection counts. It is comparatively small and suitable for CPU-first exploration of Triton model serving, image preprocessing and postprocessing. The currently maintained ONNX Model Zoo location is the `onnxmodelzoo` organization on Hugging Face; the historic `onnx/models` GitHub repository says model LFS downloads ended July 1, 2025.

- Model file: `ssd_mobilenet_v1_12.onnx`
- Model repository: https://huggingface.co/onnxmodelzoo/ssd_mobilenet_v1_12/tree/main
- Model card: https://huggingface.co/onnxmodelzoo/ssd_mobilenet_v1_12
- Historic upstream documentation: https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/ssd-mobilenetv1/README.md
- Model file size shown by Hugging Face: approximately **29.5 MB** (unverified locally).
- Verified upstream file page: https://huggingface.co/onnxmodelzoo/ssd_mobilenet_v1_12/blob/main/ssd_mobilenet_v1_12.onnx
- Direct artifact URL (to be validated from the VM): https://huggingface.co/onnxmodelzoo/ssd_mobilenet_v1_12/resolve/main/ssd_mobilenet_v1_12.onnx
- **Expected upstream SHA-256 (Hugging Face file metadata):** `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058`. Actual downloaded file must be hashed and matched before use.
- Model card lists ONNX opset **12**, batch size **1**, and input as NHWC with 3 channels and `uint8` image values; example input tensor: `image_tensor:0`.
- Four documented outputs: `num_detections:0`, `detection_boxes:0`, `detection_scores:0`, and `detection_classes:0`.
- Output bounding boxes are normalized relative to the source image; class labels are COCO categories.
- **License metadata discrepancy to reconcile:** the Hugging Face model card labels the repository **Apache-2.0**; the historic upstream model-specific README says **MIT License**. Both are permissive, but record provenance and review files before redistribution.

## Intended first experiment

1. Create versioned Triton repository path `model_repository/ssd_mobilenet_v1_12/1/`.
2. Download the actual ONNX file from the authoritative Hugging Face model repository into the VM, record exact source URL and local SHA-256 checksum.
3. Inspect actual graph input/output names, shapes and dtypes; do not infer they match the model card until observed.
4. Write explicit `config.pbtxt` using `backend: "onnxruntime"`, `instance_group { count: 1 kind: KIND_CPU }`, and `max_batch_size: 0` initially unless the observed graph indicates a better specification. **No dynamic batching claims until actual testing.**
5. Perform a controlled Triton restart (initial server was started with `MODE_NONE` and the model repository was empty at startup), check backend/model table and `/v2/models/.../ready`.
6. Perform deterministic local test inference and only then implement image preprocessing/drawing of boxes. Keep HTTP bound to host loopback.
7. Track source license/version/hash and report observed timing separately from benchmark claims.

NVIDIA Triton documentation on CPU instance groups: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html

**Caution:** Model license metadata, graph, ONNX operators, ONNX Runtime CPU execution provider support, and Triton backend load remain subjects for **actual validation**. Do not publish model binary in the learning repository by default.

## Artifact verification on Azure VM

- Local SHA-256 verified after `curl` transfer: `b8fba5e404077d4048d27fcd1667e85e27e192eb9bf51e696c46a3acd7d21058` — **matches upstream digest exactly**.
- Local path: `/home/azureuser/dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx`.
- Next: Inspect real ONNX graph I/O and opset. Runtime compatibility, backend loading, and inference remain unverified.


## Verified ONNX graph metadata — 2026-11-04

Parser: ONNX 1.19.1; graph IR version **7**, default ONNX opset **12**. `onnx.checker.check_model(model)` **PASSED**.

| IO | Actual tensor name | ONNX dtype | ONNX shape (symbolic identifiers preserved) |
|---|---|---|---|
| Input | `inputs` | UINT8 | `['unk__6578', 'unk__6579', 'unk__6580', 3]` |
| Output | `detection_boxes` | FLOAT | `['unk__6581', 'unk__6582', 4]` |
| Output | `detection_classes` | FLOAT | `['unk__6583', 'unk__6584']` |
| Output | `detection_scores` | FLOAT | `['unk__6585', 'unk__6586']` |
| Output | `num_detections` | FLOAT | `['unk__6587']` |

Input is rank 4 and channels-last (last dimension 3). All other dimensions are symbolic/unspecified, and the model graph has distinct symbolic IDs, so do not assume equal shapes without inference tests. Inspected tensor names supersede the names cited in older upstream documentation. Upstream file SHA-256 was independently verified earlier.

The initial version-controlled Triton configuration is [`model_repository/ssd_mobilenet_v1_12/config.pbtxt`](../../model_repository/ssd_mobilenet_v1_12/config.pbtxt). It specifies a single CPU instance and `max_batch_size: 0`, avoiding claims of Triton dynamic batching. The config has **not yet been installed or validated on the Azure VM**. Triton model loading, CPU provider support and inference correctness remain pending.

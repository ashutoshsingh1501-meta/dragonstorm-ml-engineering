#!/usr/bin/env python3
"""Reproducible experimental SSD-MobileNetV1-12 photo inference on Triton CPU.

Source image (download separately to VM, do not redistribute without verifying license):
https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg

Requires Pillow==11.3.0 and numpy in the existing isolated Python venv.
Uses a direct RGB resize to 300x300 as an INITIAL functional baseline.
This STRETCHES aspect ratio; preprocessing equivalence, accurate box coordinates,
class label indexing and detection quality are not yet established.

Run on VM:
  ~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/real_photo_triton_inference.py
"""
import http.client
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

MODEL = "ssd_mobilenet_v1_12"
HOST = "127.0.0.1"
PORT = 8000
IMAGE_PATH = Path.home() / "dragonstorm-lab" / "test-dog.jpg"
OUTPUT_NAMES = ("detection_boxes", "detection_classes", "detection_scores", "num_detections")


def preprocess(path):
    with Image.open(path) as photo:
        photo.load()
        original = photo.size
        rgb = photo.convert("RGB")
        resized = rgb.resize((300, 300), Image.Resampling.BILINEAR)
        tensor = np.expand_dims(np.asarray(resized, dtype=np.uint8), 0)
    if tensor.shape != (1, 300, 300, 3) or tensor.dtype != np.uint8:
        raise ValueError(f"Unexpected input tensor shape/dtype: {tensor.shape} / {tensor.dtype}")
    print(f"Photo: {path.name}, original WxH: {original}, resized WxH: (300, 300)")
    print(f"Input: UINT8 shape={list(tensor.shape)}, bytes={tensor.nbytes}, min={int(tensor.min())}, max={int(tensor.max())}")
    print("Preprocessing caveat: direct resize distorts aspect ratio; model-specific contract unverified.")
    return tensor


def infer(tensor):
    req = {
        "inputs": [{
            "name": "inputs",
            "shape": list(tensor.shape),
            "datatype": "UINT8",
            "parameters": {"binary_data_size": int(tensor.nbytes)},
        }],
        "outputs": [
            {"name": name, "parameters": {"binary_data": True}}
            for name in OUTPUT_NAMES
        ],
    }
    request_header = json.dumps(req, separators=(",", ":")).encode("utf-8")
    body = request_header + tensor.tobytes(order="C")
    conn = http.client.HTTPConnection(HOST, PORT, timeout=90)
    try:
        conn.request(
            "POST",
            f"/v2/models/{MODEL}/infer",
            body=body,
            headers={
                "Content-Type": "application/octet-stream",
                "Inference-Header-Content-Length": str(len(request_header)),
            },
        )
        resp = conn.getresponse()
        status = resp.status
        header_len = resp.getheader("Inference-Header-Content-Length")
        data = resp.read()
    finally:
        conn.close()

    print("HTTP status:", status)
    if status != 200:
        raise RuntimeError(f"Triton inference failed: {data[:1500].decode('utf-8', 'replace')}")
    if header_len is None:
        raise ValueError("Missing binary response header length")
    n = int(header_len)
    if n <= 0 or n > len(data):
        raise ValueError("Bad binary response header length")
    meta = json.loads(data[:n])
    print("Model:", meta.get("model_name"), "version:", meta.get("model_version"))
    binary = memoryview(data)[n:]
    offset = 0
    arrays = {}
    for item in meta.get("outputs", []):
        name, shape, dtype = item["name"], item["shape"], item["datatype"]
        nbytes = int(item.get("parameters", {})["binary_data_size"])
        if name not in OUTPUT_NAMES or dtype != "FP32":
            raise ValueError(f"Unexpected output name/type: {name}/{dtype}")
        expected = int(np.prod(shape, dtype=np.int64)) * 4
        if nbytes != expected or offset + nbytes > len(binary):
            raise ValueError(f"Binary size mismatch for {name}")
        arr = np.frombuffer(binary[offset:offset + nbytes], dtype="<f4").reshape(shape).copy()
        if not np.isfinite(arr).all():
            raise ValueError(f"Nonfinite values in output {name}")
        arrays[name] = arr
        offset += nbytes
        print(f"  {name}: FP32 shape={shape}")
    if set(arrays) != set(OUTPUT_NAMES) or offset != len(binary):
        raise ValueError("Output names or payload length mismatch")
    return arrays


def summarize(outputs):
    counts = outputs["num_detections"]
    boxes = outputs["detection_boxes"]
    classes = outputs["detection_classes"]
    scores = outputs["detection_scores"]
    if counts.shape != (1,) or len(scores.shape) != 2 or scores.shape[0] != 1:
        raise ValueError("Unexpected per-image detection shape")
    slots = scores.shape[1]
    if classes.shape != (1, slots) or boxes.shape != (1, slots, 4):
        raise ValueError("Detection outputs differ in candidate count")
    n = float(counts[0])
    print(f"Reported num_detections: {n:g}; candidate slots: {slots}")
    print("Highest-scoring returned slots (raw class IDs, raw box coordinates):")
    for idx in np.argsort(-scores[0], kind="stable")[:min(5, slots)]:
        print(f"  slot={int(idx)} score={float(scores[0, idx]):.6f}"
              f" class_id={float(classes[0, idx]):g}"
              f" box={boxes[0, idx].tolist()}")
    print("NOTE: Do not interpret raw class IDs or box coordinates as labels/pixels without validating model conventions.")
    print("REAL PHOTO INFERENCE SMOKE TEST PASSED (prediction correctness NOT yet validated).")


def main():
    tensor = preprocess(IMAGE_PATH)
    outputs = infer(tensor)
    summarize(outputs)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError) as exc:
        print(f"REAL PHOTO INFERENCE FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)

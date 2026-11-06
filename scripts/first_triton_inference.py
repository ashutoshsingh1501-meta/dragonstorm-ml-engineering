#!/usr/bin/env python3
"""First Triton CPU inference smoke test for SSD-MobileNetV1-12.

Sends a deterministic BLACK synthetic uint8 NHWC image through Triton's V2 HTTP
binary tensor protocol. This tests serving/inference mechanics, NOT object
detection accuracy or meaningful predictions. The request stays on VM localhost.

Run (after downloading this script onto the Azure VM):
    ~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/first_triton_inference.py

Dependencies: Python 3.12 standard library and NumPy in the isolated venv.
Model: ssd_mobilenet_v1_12, version 1; Triton 2.74.0, CPU instance.
"""
import http.client
import json
import sys

import numpy as np

MODEL = "ssd_mobilenet_v1_12"
OUTPUT_NAMES = (
    "detection_boxes",
    "detection_classes",
    "detection_scores",
    "num_detections",
)
INPUT_SHAPE = (1, 300, 300, 3)  # Experimental size; actual model input is dynamic NHWC.


def run() -> int:
    # Synthetic sample verifies runtime execution. All-black pixels are NOT
    # suitable for assessing classification/detection quality.
    image = np.zeros(INPUT_SHAPE, dtype=np.uint8)
    metadata = {
        "inputs": [
            {
                "name": "inputs",
                "shape": list(image.shape),
                "datatype": "UINT8",
                "parameters": {"binary_data_size": image.nbytes},
            }
        ],
        "outputs": [
            {"name": name, "parameters": {"binary_data": True}}
            for name in OUTPUT_NAMES
        ],
    }
    header = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    payload = header + image.tobytes(order="C")

    print("Test input: synthetic all-black image (NOT an accuracy test)")
    print(f"Input tensor: dtype=UINT8, shape={list(image.shape)}, bytes={image.nbytes}")
    print(f"POST http://127.0.0.1:8000/v2/models/{MODEL}/infer")

    connection = http.client.HTTPConnection("127.0.0.1", 8000, timeout=90)
    try:
        connection.request(
            "POST",
            f"/v2/models/{MODEL}/infer",
            body=payload,
            headers={
                "Content-Type": "application/octet-stream",
                "Inference-Header-Content-Length": str(len(header)),
            },
        )
        response = connection.getresponse()
        response_bytes = response.read()
        status = response.status
        response_header_size = response.getheader("Inference-Header-Content-Length")
    finally:
        connection.close()

    print(f"HTTP status: {status}")
    if status != 200:
        print("Server error response:", response_bytes[:5000].decode("utf-8", "replace"))
        return 1
    if response_header_size is None:
        print("ERROR: Triton did not return binary response header length.")
        print(response_bytes[:1000].decode("utf-8", "replace"))
        return 1

    header_bytes = int(response_header_size)
    if header_bytes <= 0 or header_bytes > len(response_bytes):
        raise ValueError("Invalid Triton inference response header length")

    result = json.loads(response_bytes[:header_bytes])
    binary_data = memoryview(response_bytes)[header_bytes:]
    offset = 0
    received = set()

    print("Model:", result.get("model_name"), "version:", result.get("model_version"))
    for output in result.get("outputs", []):
        name = output["name"]
        shape = output["shape"]
        dtype = output["datatype"]
        size = int(output.get("parameters", {})["binary_data_size"])
        if size < 0 or offset + size > len(binary_data):
            raise ValueError(f"Invalid binary payload length for {name}")
        if dtype != "FP32":
            raise ValueError(f"Unexpected datatype {dtype} for {name}")
        elements = int(np.prod(shape, dtype=np.int64))
        if size != elements * np.dtype("<f4").itemsize:
            raise ValueError(f"Size/shape mismatch for {name}: {size} vs {shape}")

        array = np.frombuffer(binary_data[offset:offset + size], dtype="<f4").reshape(shape)
        offset += size
        received.add(name)

        print(f"  {name}: dtype={dtype}, shape={shape}, elements={array.size}")
        if array.size:
            print(f"    sample first 5 values: {array.flat[:5].tolist()}")
            print(f"    finite values: {int(np.count_nonzero(np.isfinite(array)))}/{array.size}")

    if received != set(OUTPUT_NAMES):
        raise ValueError(f"Output set mismatch. Expected {OUTPUT_NAMES}, got {sorted(received)}")
    if offset != len(binary_data):
        raise ValueError(f"Unconsumed binary response bytes: {len(binary_data) - offset}")

    print("SMOKE TEST PASSED: Inference HTTP response and four output tensors decoded.")
    print("NOTE: Synthetic black-image predictions do not validate detection accuracy.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"SMOKE TEST FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)

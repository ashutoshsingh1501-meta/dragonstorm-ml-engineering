"""D4-06/D4-07: observed Triton CPU inference baseline and concurrency test.

Dependencies: Python 3, numpy, Pillow, running localhost Triton model, test-dog.jpg.
This measures client HTTP request latency (NOT backend-only compute time).
Run: ~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/benchmark_triton.py
"""
import http.client
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image

HOST = "127.0.0.1"
PORT = 8000
MODEL = "ssd_mobilenet_v1_12"
LAB = Path.home() / "dragonstorm-lab"
WARMUP = 5
SEQUENTIAL = 30
CONCURRENT_REQUESTS = 24

def prepare_inputs():
    with Image.open(LAB / "test-dog.jpg") as img:
        rgb = img.convert("RGB")
        original = np.expand_dims(np.asarray(rgb, dtype=np.uint8), 0).copy()
        resized = np.expand_dims(np.asarray(rgb.resize((300,300), Image.Resampling.BILINEAR), dtype=np.uint8), 0).copy()
    return {"pillow_300": resized, "original_resolution": original}

def infer(tensor):
    payload = tensor.tobytes()
    header = {
        "inputs": [{
            "name": "inputs", "shape": list(tensor.shape), "datatype": "UINT8",
            "parameters": {"binary_data_size": len(payload)}
        }],
        "outputs": [
            {"name": name, "parameters": {"binary_data": True}}
            for name in ("detection_boxes", "detection_classes", "detection_scores", "num_detections")
        ],
    }
    encoded = json.dumps(header).encode("utf-8")
    body = encoded + payload
    conn = http.client.HTTPConnection(HOST, PORT, timeout=30)
    start = time.perf_counter()
    try:
        conn.request("POST", f"/v2/models/{MODEL}/infer", body=body, headers={
            "Content-Type": "application/octet-stream",
            "Inference-Header-Content-Length": str(len(encoded))
        })
        response = conn.getresponse()
        status = response.status
        result = response.read()
        header_length = response.getheader("Inference-Header-Content-Length")
        elapsed = time.perf_counter() - start
        if status != 200:
            raise RuntimeError(f"Triton HTTP {status}: {result[:300].decode('utf-8', 'replace')}")
        if not header_length:
            raise RuntimeError("Missing Triton response header length")
        length = int(header_length)
        metadata = json.loads(result[:length])
        if metadata.get("error"):
            raise RuntimeError(metadata["error"])
        output_names = {output["name"] for output in metadata.get("outputs", [])}
        expected = {"detection_boxes", "detection_classes", "detection_scores", "num_detections"}
        if not expected.issubset(output_names):
            raise RuntimeError(f"Missing output tensors: {expected - output_names}")
        expected_bytes = sum(int(out.get("parameters", {}).get("binary_data_size", 0)) for out in metadata["outputs"])
        if len(result) - length != expected_bytes:
            raise RuntimeError("Unexpected binary output payload size")
        return elapsed * 1000
    finally:
        conn.close()

def percentile(values, p):
    return float(np.percentile(values, p))

def report(name, values, wall_seconds):
    values = sorted(values)
    record = {
        "test": name, "requests": len(values),
        "mean_ms": round(statistics.mean(values), 3),
        "p50_ms": round(percentile(values,50), 3),
        "p95_ms": round(percentile(values,95), 3),
        "p99_ms": round(percentile(values,99), 3),
        "min_ms": round(min(values),3),
        "max_ms": round(max(values),3),
        "throughput_rps": round(len(values)/wall_seconds,2),
    }
    print(json.dumps(record, indent=2))
    return record

def sequential_test(name, tensor):
    print(f"\n=== SEQUENTIAL: {name} ===")
    for _ in range(WARMUP): infer(tensor)
    values = []
    start = time.perf_counter()
    for _ in range(SEQUENTIAL): values.append(infer(tensor))
    return report(name+"_sequential", values, time.perf_counter()-start)

def concurrent_test(name, tensor, workers):
    print(f"\n=== CONCURRENCY: {name}, clients={workers} ===")
    for _ in range(WARMUP): infer(tensor)
    values = []
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(infer, tensor) for _ in range(CONCURRENT_REQUESTS)]
        for future in as_completed(futures): values.append(future.result())
    return report(f"{name}_concurrency_{workers}", values, time.perf_counter()-start)

def main():
    print("=== DRAGONSTORM TRITON CPU BENCHMARK ===")
    print("Model:", MODEL)
    print("Warm-up:", WARMUP)
    print("Sequential requests:", SEQUENTIAL)
    print("Concurrent requests:", CONCURRENT_REQUESTS)
    inputs = prepare_inputs()
    results = []
    for name, tensor in inputs.items():
        print(f"\nInput: {name}", "shape:", list(tensor.shape), "bytes:", tensor.nbytes)
        results.append(sequential_test(name, tensor))
    for workers in (1, 2, 4):
        results.append(concurrent_test("pillow_300", inputs["pillow_300"], workers))
    output = LAB / "d4-triton-benchmark-results.json"
    output.write_text(json.dumps({"model": MODEL, "warmup": WARMUP, "results": results}, indent=2), encoding="utf-8")
    print("\nResults saved:", output)
    print("D4 TRITON BENCHMARK COMPLETE")

if __name__ == "__main__":
    main()

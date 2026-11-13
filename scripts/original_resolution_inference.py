"""D4-03: original-resolution inference without external resizing.

Requires test-dog.jpg and real_photo_triton_inference.py next to VM lab scripts.
Run: ~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/original_resolution_inference.py
"""
from pathlib import Path
from time import perf_counter
import numpy as np
from PIL import Image
from real_photo_triton_inference import infer, summarize

LAB = Path.home() / "dragonstorm-lab"
IMAGE = LAB / "test-dog.jpg"

def main():
    print("=== DRAGONSTORM D4-03 ===")
    print("Experiment: Original-resolution inference")
    with Image.open(IMAGE) as photo:
        rgb = photo.convert("RGB")
        width, height = rgb.size
        tensor = np.expand_dims(np.asarray(rgb, dtype=np.uint8), axis=0).copy()
    print(f"Original image: {width}x{height}")
    print(f"Input shape: {list(tensor.shape)}")
    print(f"Input datatype: {tensor.dtype}")
    print(f"Input bytes: {tensor.nbytes:,}")
    print("\n=== TRITON INFERENCE ===")
    start = perf_counter()
    try:
        outputs = infer(tensor)
    except Exception as exc:
        elapsed = perf_counter() - start
        print(f"Inference failed after {elapsed:.3f}s")
        print(f"Error: {type(exc).__name__}: {exc}")
        raise
    print(f"Inference elapsed: {perf_counter()-start:.3f}s")
    print("\n=== DETECTION RESULTS ===")
    summarize(outputs)
    print("\nORIGINAL RESOLUTION INFERENCE: PASSED")

if __name__ == "__main__":
    main()

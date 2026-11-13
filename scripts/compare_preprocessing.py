"""D4-05: compare original, Pillow and ONNX-like asymmetric resizing.

Run: ~/dragonstorm-lab/.venv-onnx-inspect/bin/python ~/dragonstorm-lab/compare_preprocessing.py
No OpenCV/SciPy required. C is an approximation: ONNX internal resize uses
floating pixels, C rounds external interpolation to UINT8.
"""
from pathlib import Path
from time import perf_counter
import numpy as np
from PIL import Image
from real_photo_triton_inference import infer, summarize

LAB = Path.home() / "dragonstorm-lab"
IMAGE = LAB / "test-dog.jpg"
TARGET_H = TARGET_W = 300

def asymmetric_bilinear(image, target_h, target_w):
    src_h, src_w, channels = image.shape
    ys = np.arange(target_h, dtype=np.float64) * src_h / target_h
    xs = np.arange(target_w, dtype=np.float64) * src_w / target_w
    y0 = np.floor(ys).astype(np.int64)
    x0 = np.floor(xs).astype(np.int64)
    y1 = np.minimum(y0 + 1, src_h - 1)
    x1 = np.minimum(x0 + 1, src_w - 1)
    wy = (ys - y0)[:, None, None]
    wx = (xs - x0)[None, :, None]
    source = image.astype(np.float32)
    top_left = source[y0[:, None], x0[None, :]]
    top_right = source[y0[:, None], x1[None, :]]
    bottom_left = source[y1[:, None], x0[None, :]]
    bottom_right = source[y1[:, None], x1[None, :]]
    top = top_left * (1-wx) + top_right * wx
    bottom = bottom_left * (1-wx) + bottom_right * wx
    return np.clip(np.rint(top * (1-wy) + bottom * wy), 0, 255).astype(np.uint8)

def run_variant(name, image):
    tensor = np.expand_dims(np.ascontiguousarray(image, dtype=np.uint8), axis=0)
    print(f"\n=== {name} ===")
    print("Input shape:", list(tensor.shape))
    print("Input bytes:", tensor.nbytes)
    start = perf_counter()
    outputs = infer(tensor)
    print(f"Client elapsed: {perf_counter()-start:.4f}s")
    summarize(outputs)
    return outputs

def main():
    print("=== DRAGONSTORM D4-05 ===")
    with Image.open(IMAGE) as photo:
        rgb = photo.convert("RGB")
        original = np.asarray(rgb, dtype=np.uint8).copy()
        pillow_resized = np.asarray(rgb.resize((TARGET_W, TARGET_H), Image.Resampling.BILINEAR), dtype=np.uint8).copy()
    onnx_like = asymmetric_bilinear(original, TARGET_H, TARGET_W)
    print("Original image:", original.shape)
    difference = np.abs(pillow_resized.astype(np.int16) - onnx_like.astype(np.int16))
    print("\n=== PIXEL COMPARISON ===")
    print("Mean absolute difference:", float(difference.mean()))
    print("Maximum pixel difference:", int(difference.max()))
    print("Different channel values:", int(np.count_nonzero(difference)))
    print("Total channel values:", difference.size)
    Image.fromarray(pillow_resized).save(LAB / "d4-05-pillow-300.jpg")
    Image.fromarray(onnx_like).save(LAB / "d4-05-asymmetric-300.jpg")
    run_variant("A: ORIGINAL RESOLUTION", original)
    run_variant("B: PILLOW BILINEAR 300x300", pillow_resized)
    run_variant("C: ASYMMETRIC BILINEAR 300x300", onnx_like)
    print("\nD4-05 COMPARISON COMPLETE")

if __name__ == "__main__":
    main()

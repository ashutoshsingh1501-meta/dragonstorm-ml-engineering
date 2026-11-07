#!/usr/bin/env python3
"""Annotate a real SSD-MobileNetV1 detection using verified COCO IDs.

Experimental baseline: uses existing real_photo_triton_inference.preprocess,
which stretches the 1546x1213 photo to 300x300 before inference. Boxes are
reported normalized as [top,left,bottom,right], per upstream SSD-MobileNetV1
README. They are mapped back onto the original image for visualization.
This is not a measured accuracy or model calibration experiment.

Dependencies: existing Pillow 11.3.0, NumPy, and the same-folder
real_photo_triton_inference.py in isolated Python environment.
External files already downloaded on VM:
  ~/dragonstorm-lab/test-dog.jpg
  ~/dragonstorm-lab/mscoco_label_map.pbtxt
Output stays local to VM:
  ~/dragonstorm-lab/test-dog-annotated.jpg

Run:
  ~/dragonstorm-lab/.venv-onnx-inspect/bin/python \
    ~/dragonstorm-lab/annotate_triton_detection.py
"""
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from real_photo_triton_inference import IMAGE_PATH, infer, preprocess

HOME_LAB = Path.home() / "dragonstorm-lab"
LABEL_FILE = HOME_LAB / "mscoco_label_map.pbtxt"
OUTPUT_FILE = HOME_LAB / "test-dog-annotated.jpg"
MIN_SCORE = 0.50


def read_coco_map(path):
    contents = path.read_text(encoding="utf-8")
    blocks = re.findall(r"item\s*\{[^}]*\}", contents, flags=re.DOTALL)
    labels = {}
    for block in blocks:
        id_match = re.search(r"\bid\s*:\s*(\d+)\b", block)
        label_match = re.search(r"\bdisplay_name\s*:\s*\"([^\"]+)\"", block)
        if id_match and label_match:
            id_value = int(id_match.group(1))
            if id_value in labels:
                raise ValueError(f"Duplicate COCO ID {id_value} in source label map")
            labels[id_value] = label_match.group(1)
    if labels.get(17) != "cat" or labels.get(18) != "dog" or labels.get(19) != "horse":
        raise ValueError("Local COCO category mapping did not match verified IDs 17–19")
    print(f"COCO source mapping: 17={labels[17]}, 18={labels[18]}, 19={labels[19]}")
    return labels


def draw_result(boxes, classes, scores, counts, labels, source_path, output_path):
    if boxes.ndim != 3 or boxes.shape[0] != 1 or boxes.shape[-1] != 4:
        raise ValueError("Unexpected shape for detection_boxes")
    if classes.shape != scores.shape or classes.shape[0] != 1:
        raise ValueError("Incompatible class/score shapes")
    if boxes.shape[1] != scores.shape[1] or counts.shape != (1,):
        raise ValueError("Inconsistent number of detection slots")
    count_float = float(counts[0])
    count = int(count_float)
    if count_float != count or count < 0 or count > scores.shape[1]:
        raise ValueError(f"Invalid num_detections value {count_float}")

    with Image.open(source_path) as original:
        canvas = original.convert("RGB")
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    drawn = 0
    print(f"Input image: {width}x{height}; reported detections: {count}")
    for i in range(count):
        score = float(scores[0, i])
        if score < MIN_SCORE:
            continue
        raw_class = float(classes[0, i])
        if not np.isfinite(raw_class) or raw_class != int(raw_class):
            raise ValueError(f"Unexpected class ID {raw_class}")
        class_id = int(raw_class)
        label = labels.get(class_id)
        if label is None:
            raise ValueError(f"COCO label map missing detected class ID {class_id}")
        top, left, bottom, right = map(float, boxes[0, i])
        if not all(np.isfinite([top, left, bottom, right])):
            raise ValueError("Non-finite bounding-box value")
        if not (0 <= top < bottom <= 1 and 0 <= left < right <= 1):
            raise ValueError(f"Invalid normalized box {boxes[0, i].tolist()}")

        left_px = round(left * width)
        right_px = round(right * width)
        top_px = round(top * height)
        bottom_px = round(bottom * height)
        draw.rectangle([left_px, top_px, right_px, bottom_px], outline="red", width=6)
        caption = f"{label}  {score:.2%} (class {class_id})"
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        label_y = max(0, top_px - text_h - 12)
        draw.rectangle([left_px, label_y, left_px + text_w + 12, label_y + text_h + 10],
                       fill="red")
        draw.text((left_px + 6, label_y + 4), caption, fill="white", font=font)
        drawn += 1
        print(f"Detection {i}: {caption}")
        print(f"  normalized TLBR: {[top, left, bottom, right]}")
        print(f"  original-image pixel LTRB: {[left_px, top_px, right_px, bottom_px]}")
    if drawn == 0:
        raise ValueError(f"No detections above score threshold {MIN_SCORE}")
    canvas.save(output_path, format="JPEG", quality=92)
    print(f"Annotated image saved: {output_path}")
    print(f"Drawn detections: {drawn}")
    print("CAVEAT: Input image was stretched to 300x300 during inference;")
    print("mapped box visualization does not validate geometric or detection accuracy.")
    print("ANNOTATION SMOKE TEST PASSED")


def main():
    labels = read_coco_map(LABEL_FILE)
    tensor = preprocess(IMAGE_PATH)
    outputs = infer(tensor)
    draw_result(outputs["detection_boxes"], outputs["detection_classes"],
                outputs["detection_scores"], outputs["num_detections"],
                labels, IMAGE_PATH, OUTPUT_FILE)


if __name__ == "__main__":
    main()

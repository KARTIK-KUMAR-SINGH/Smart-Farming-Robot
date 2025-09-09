#!/usr/bin/env python3
import cv2
import numpy as np
from edge_impulse_linux.runner import ImpulseRunner

MODEL_FILE = '/home/kartik/robot/vegetable-detection-linux-aarch64-v2.eim'

def main():
    runner = ImpulseRunner(MODEL_FILE)
    model_info = runner.init()
    print("? Model loaded:", model_info['project']['name'])

    h = model_info['model_parameters']['image_input_height']
    w = model_info['model_parameters']['image_input_width']
    labels = model_info['model_parameters']['labels']
    print(f"Expecting input shape: ({h},{w},1) with labels {labels}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("? Could not open camera")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocess ? grayscale ? flatten
            resized = cv2.resize(frame, (w, h))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            features = np.float32(gray).flatten() / 255.0

            # Run inference
            res = runner.classify(features)

            if "result" in res:
                # For object detection models
                boxes = res["result"].get("bounding_boxes", [])
                if boxes:
                    print("Detections:")
                    for b in boxes:
                        label = b["label"]
                        score = b["value"]
                        x = b["x"]
                        y = b["y"]
                        w_box = b["width"]
                        h_box = b["height"]
                        print(f"  {label} ({score:.2f}) at x={x}, y={y}, w={w_box}, h={h_box}")

    finally:
        cap.release()
        runner.stop()

if __name__ == "__main__":
    main()

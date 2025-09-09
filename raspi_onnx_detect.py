#!/usr/bin/env python3
import cv2
import numpy as np
import onnxruntime as ort
from flask import Flask, Response

# Load ONNX model
model_path = "best.onnx"
session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Open webcam
cap = cv2.VideoCapture(0)

app = Flask(__name__)

def non_max_suppression(boxes, scores, iou_threshold=0.5):
    """Simple NMS implementation"""
    idxs = scores.argsort()[::-1]
    keep = []
    while len(idxs) > 0:
        current = idxs[0]
        keep.append(current)
        if len(idxs) == 1:
            break
        ious = []
        for i in idxs[1:]:
            # Compute IoU
            xx1 = max(boxes[current][0], boxes[i][0])
            yy1 = max(boxes[current][1], boxes[i][1])
            xx2 = min(boxes[current][2], boxes[i][2])
            yy2 = min(boxes[current][3], boxes[i][3])
            w = max(0, xx2 - xx1)
            h = max(0, yy2 - yy1)
            inter = w * h
            union = (
                (boxes[current][2] - boxes[current][0])
                * (boxes[current][3] - boxes[current][1])
                + (boxes[i][2] - boxes[i][0])
                * (boxes[i][3] - boxes[i][1])
                - inter
            )
            iou = inter / union if union > 0 else 0
            ious.append(iou)
        ious = np.array(ious)
        idxs = idxs[1:][ious < iou_threshold]
    return keep

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
        img = np.expand_dims(img, axis=0)
        input_tensor = img.copy()

        # Inference
        outputs = session.run([output_name], {input_name: input_tensor})[0]  # (1, 5, 8400)
        outputs = np.squeeze(outputs).T  # shape -> (8400, 5)

        boxes = []
        scores = []

        for pred in outputs:
            x, y, w_box, h_box, conf = pred
            if conf > 0.5:  # confidence threshold
                # Convert from center x,y,w,h to x1,y1,x2,y2 in original image scale
                x1 = int((x - w_box / 2) * w / 640)
                y1 = int((y - h_box / 2) * h / 640)
                x2 = int((x + w_box / 2) * w / 640)
                y2 = int((y + h_box / 2) * h / 640)
                boxes.append([x1, y1, x2, y2])
                scores.append(conf)

        if len(boxes) > 0:
            boxes = np.array(boxes)
            scores = np.array(scores)
            keep = non_max_suppression(boxes, scores)

            for i in keep:
                x1, y1, x2, y2 = boxes[i]
                conf = scores[i]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Pencil {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

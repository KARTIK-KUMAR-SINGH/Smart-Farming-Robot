#!/usr/bin/env python3
"""
predict_stream_ei.py
Live Raspberry Pi camera stream with Edge Impulse model predictions overlaid.

Requirements:
    pip install flask opencv-python-headless edge-impulse-linux numpy
"""

import cv2
import time
import threading
from flask import Flask, Response
from edge_impulse_linux.image import ImageImpulseRunner

# Path to your .eim model
MODEL_PATH = "./vegetable-detection-linux-armv7-v1.eim"

# Initialize Flask app
app = Flask(__name__)
output_frame = None
lock = threading.Lock()


def capture_and_predict():
    global output_frame

    # Load the Edge Impulse model
    with ImageImpulseRunner(MODEL_PATH) as runner:
        model_info = runner.init()
        labels = model_info['model_parameters']['labels']
        print("Labels:", labels)

        # Open the Pi camera (0 is default)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print("Cannot open camera")
            return

        print("Starting live predictions...")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Convert frame to RGB for EI
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Run inference
            features = runner.get_features_from_image(rgb_frame)
            res = runner.classify(features)

            # Overlay predictions on frame
            predictions = res['classification']
            y0 = 30
            for label in labels:
                conf = predictions.get(label, 0.0)
                text = f"{label}: {conf*100:.1f}%"
                cv2.putText(frame, text, (10, y0),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y0 += 30

            # Save the frame for streaming
            with lock:
                output_frame = frame.copy()

        cap.release()


def generate():
    global output_frame
    while True:
        with lock:
            if output_frame is None:
                continue
            # Encode frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', output_frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # Start camera thread
    t = threading.Thread(target=capture_and_predict, daemon=True)
    t.start()

    print("Open browser at http://<pi_ip>:5000/video to view live stream")
    app.run(host='0.0.0.0', port=5000, threaded=True)

#!/usr/bin/env python3
"""
capture_dataset.py
Capture dataset with live browser preview (Flask streaming).
Controls:
- In terminal:
    n / p : next/previous class
    c     : capture frame
    a     : toggle auto-capture
    q     : quit
- In browser: just view live feed at http://<pi_ip>:5000/video
"""

import cv2, os, time, argparse, glob, threading
from flask import Flask, Response

# ------------------------
# Parse arguments
# ------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--outdir", default="data", help="base output dir")
parser.add_argument("--classes", default="", help="comma separated class names")
parser.add_argument("--w", type=int, default=640, help="camera width")
parser.add_argument("--h", type=int, default=480, help="camera height")
parser.add_argument("--interval", type=float, default=1.0, help="auto-capture interval (sec)")
args = parser.parse_args()

if not args.classes:
    classes = input("Enter classes (comma separated, e.g. tomato,potato): ").strip().split(",")
    classes = [c.strip() for c in classes if c.strip()]
else:
    classes = [c.strip() for c in args.classes.split(",") if c.strip()]

if not classes:
    print("No classes given. Exiting.")
    exit(1)

outdir = os.path.abspath(args.outdir)
os.makedirs(outdir, exist_ok=True)
for c in classes:
    os.makedirs(os.path.join(outdir, c), exist_ok=True)

# ------------------------
# Initialize camera
# ------------------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.h)

if not cap.isOpened():
    print("? Cannot open camera")
    exit(1)

# ------------------------
# Flask App for Streaming
# ------------------------
app = Flask(__name__)

def generate():
    while True:
        success, frame = cap.read()
        if not success:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run Flask in background thread
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# ------------------------
# Dataset Capture Loop
# ------------------------
counts = {c: len(glob.glob(os.path.join(outdir, c, "*.jpg"))) for c in classes}
curr_idx, auto_mode, last_saved = 0, False, 0.0

print("? Capturing... Open browser at http://<pi_ip>:5000/video to view stream")
print("Controls in terminal: n=next, p=prev, c=capture, a=toggle auto, q=quit")

while True:
    ret, frame = cap.read()
    if not ret:
        time.sleep(0.2)
        continue

    label = classes[curr_idx]

    # Auto-save
    if auto_mode and (time.time() - last_saved >= args.interval):
        fname = os.path.join(outdir, label, f"{label}_{counts[label]:06d}.jpg")
        cv2.imwrite(fname, frame)
        counts[label] += 1
        last_saved = time.time()
        print("Auto saved:", fname)

    # Wait for key
    try:
        key = input(">> ").strip().lower()
    except EOFError:
        break

    if key == "q":
        break
    if key == "c":
        fname = os.path.join(outdir, label, f"{label}_{counts[label]:06d}.jpg")
        cv2.imwrite(fname, frame)
        counts[label] += 1
        print("Saved:", fname)
    if key == "a":
        auto_mode = not auto_mode
        print("Auto mode:", auto_mode)
        last_saved = time.time()
    if key == "n":
        curr_idx = (curr_idx + 1) % len(classes)
        print("? Switched to class:", classes[curr_idx])
    if key == "p":
        curr_idx = (curr_idx - 1) % len(classes)
        print("? Switched to class:", classes[curr_idx])

cap.release()
print("? Capture finished.")

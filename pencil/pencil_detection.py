# pencil_detection.py
import time
import cv2
import numpy as np
import onnxruntime as rt
from flask import Flask, Response
import threading
import serial

# -------------------------
# Config
# -------------------------
ONNX_PATH = "best.onnx"
IMG_SIZE = 640
CONF_THRESHOLD = 0.30
NMS_IOU = 0.45

# --- Globals for trigger ---
is_busy = False
confirm_count = 0
CONFIRM_FRAMES = 3   # require this many frames with conf > 0.6

# -------------------------
# Serial connection to Arduino
# -------------------------
print("[INFO] Connecting to Arduino on /dev/ttyACM0 ...")
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)   # allow Arduino to reset
ser.write(b"HOME\n")
print("[INFO] Arduino connected and set to HOME")

# -------------------------
# Utilities
# -------------------------
def print_debug(tag, val):
    print(f"[DEBUG] {tag}: {val}")

def iou(box, boxes):
    x1 = np.maximum(box[0], boxes[:,0])
    y1 = np.maximum(box[1], boxes[:,1])
    x2 = np.minimum(box[2], boxes[:,2])
    y2 = np.minimum(box[3], boxes[:,3])
    inter_w = np.maximum(0, x2 - x1)
    inter_h = np.maximum(0, y2 - y1)
    inter = inter_w * inter_h
    area1 = (box[2]-box[0])*(box[3]-box[1])
    area2 = (boxes[:,2]-boxes[:,0])*(boxes[:,3]-boxes[:,1])
    union = area1 + area2 - inter + 1e-8
    return inter / union

def simple_nms(boxes, scores, iou_thresh=0.45):
    if len(boxes) == 0:
        return []
    idxs = np.argsort(scores)[::-1]
    keep = []
    while idxs.size:
        i = idxs[0]
        keep.append(i)
        if idxs.size == 1:
            break
        rest = idxs[1:]
        ious = iou(boxes[i], boxes[rest])
        idxs = rest[ious <= iou_thresh]
    return keep

# -------------------------
# Pick sequence (Arduino moves)
# -------------------------
def pick_sequence(frame_w, frame_h, box):
    global is_busy
    is_busy = True
    cx, cy, bw, bh = box
    print(f"[ACTION] Pick sequence triggered at ({cx},{cy}), size=({bw}x{bh})")

    try:
        # Move arm above pencil
        ser.write(b"M,0,180,120,60\n")
        time.sleep(1.5)

        # Close claw to grab
        ser.write(b"M,0,180,120,20\n")
        time.sleep(1.5)

        # Lift up
        ser.write(b"M,0,20,60,20\n")
        time.sleep(1.5)

        # Rotate base to drop zone
        ser.write(b"M,180,36,90,20\n")
        time.sleep(1.5)

        # Open claw to release
        ser.write(b"M,180,36,90,60\n")
        time.sleep(1.5)

        # Return to home
        ser.write(b"HOME\n")
        time.sleep(2)

    except Exception as e:
        print("[ERROR] Failed to send commands:", e)

    is_busy = False

# -------------------------
# Load ONNX
# -------------------------
sess = rt.InferenceSession(ONNX_PATH, providers=['CPUExecutionProvider'])
input_name = sess.get_inputs()[0].name
print_debug("ONNX input name", input_name)
print_debug("ONNX input shape", sess.get_inputs()[0].shape)

# -------------------------
# Camera
# -------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera (index 0).")

# -------------------------
# Preprocess
# -------------------------
def preprocess(frame):
    img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = img.transpose(2, 0, 1)  # CHW
    img = np.expand_dims(img, 0)   # 1x3xHxW
    return img

# -------------------------
# Generator used by Flask
# -------------------------
first_debug = True

def generate():
    global first_debug, confirm_count
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h0, w0 = frame.shape[:2]

        img = preprocess(frame)
        t0 = time.time()
        outputs = sess.run(None, {input_name: img})
        t1 = time.time()

        out_arr = np.array(outputs[0])

        if first_debug:
            print_debug("raw output shape", out_arr.shape)
            first_debug = False

        arr = out_arr.copy()
        if arr.ndim == 3 and arr.shape[0] == 1:
            arr = arr[0]
        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = np.squeeze(arr)
        if arr.ndim == 2 and arr.shape[0] <= 20 and arr.shape[1] > 20:
            arr = arr.T
        if arr.ndim != 2:
            arr = arr.reshape(-1, 5)

        N, K = arr.shape
        if K == 5:
            xywh = arr[:, :4]
            confs = arr[:, 4]
            class_ids = np.zeros(N, dtype=int)
        elif K == 6:
            last_col = arr[:,5]
            if np.all((last_col >= 0.0) & (last_col <= 1.0)):
                obj_conf = arr[:,4]
                cls_conf = arr[:,5]
                confs = obj_conf * cls_conf
                xywh = arr[:, :4]
                class_ids = np.zeros(N, dtype=int)
            else:
                xywh = arr[:, :4]
                confs = arr[:, 4]
                class_ids = arr[:, 5].astype(int)
        else:
            xywh = arr[:, :4]
            obj_conf = arr[:, 4]
            class_probs = arr[:, 5:]
            class_ids = np.argmax(class_probs, axis=1)
            cls_conf = class_probs[np.arange(len(class_ids)), class_ids]
            confs = obj_conf * cls_conf

        if xywh.size == 0:
            boxes_keep = []
        else:
            xc = xywh[:,0].astype(float)
            yc = xywh[:,1].astype(float)
            ww = xywh[:,2].astype(float)
            hh = xywh[:,3].astype(float)
            max_val = np.nanmax([xc.max() if xc.size else 0,
                                 yc.max() if yc.size else 0,
                                 ww.max() if ww.size else 0,
                                 hh.max() if hh.size else 0])
            if max_val <= 1.0 + 1e-6:
                xc = xc * w0; yc = yc * h0; ww = ww * w0; hh = hh * h0
            elif max_val <= IMG_SIZE + 1e-6:
                sx = w0 / IMG_SIZE; sy = h0 / IMG_SIZE
                xc = xc * sx; ww = ww * sx; yc = yc * sy; hh = hh * sy

            x1 = np.clip(xc - ww/2.0, 0, w0-1).astype(int)
            y1 = np.clip(yc - hh/2.0, 0, h0-1).astype(int)
            x2 = np.clip(xc + ww/2.0, 0, w0-1).astype(int)
            y2 = np.clip(yc + hh/2.0, 0, h0-1).astype(int)

            boxes_all = np.stack([x1,y1,x2,y2], axis=1)
            scores_all = confs
            mask = scores_all > CONF_THRESHOLD
            if np.count_nonzero(mask) == 0:
                boxes_keep = []
            else:
                boxes_f = boxes_all[mask]
                scores_f = scores_all[mask]
                cls_f = class_ids[mask] if len(class_ids) else np.zeros(len(scores_f), dtype=int)
                keep_idx = simple_nms(boxes_f, scores_f, NMS_IOU)
                boxes_keep = [(boxes_f[i], scores_f[i], int(cls_f[i])) for i in keep_idx]

        for box, score, cid in boxes_keep:
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            label = f"Pencil {score:.2f}"
            cv2.putText(frame, label, (x1, max(y1-8,0)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            print(f"Pencil detected — conf: {score:.3f}, box: ({x1},{y1},{x2},{y2})")

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            bw = x2 - x1
            bh = y2 - y1

            global is_busy
            if score > 0.6 and not is_busy:
                confirm_count += 1
                if confirm_count >= CONFIRM_FRAMES:
                    confirm_count = 0
                    threading.Thread(
                        target=pick_sequence,
                        args=(frame.shape[1], frame.shape[0], (cx, cy, bw, bh)),
                        daemon=True
                    ).start()
            else:
                confirm_count = 0

        fps = 1.0 / (t1 - t0) if (t1 - t0) > 0 else 0
        cv2.putText(frame, f"FPS:{fps:.1f}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

# -------------------------
# Flask app
# -------------------------
app = Flask(__name__)

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Server running — open http://<pi_ip>:5000/video")
    app.run(host='0.0.0.0', port=5000)

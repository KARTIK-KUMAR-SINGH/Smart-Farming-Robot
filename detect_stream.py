from flask import Flask, Response
import cv2
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

# Load ONNX model
sess = rt.InferenceSession("/home/kartik/robot/best.onnx")

# Open camera
cap = cv2.VideoCapture(0)
CONF_THRESHOLD = 0.3

def preprocess(frame):
    img = cv2.resize(frame, (640, 640))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
    img = np.expand_dims(img, axis=0)
    return img

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        input_data = preprocess(frame)
        outputs = sess.run(None, {sess.get_inputs()[0].name: input_data})

        # outputs[0] shape: [1, num_boxes, 6] -> [x1, y1, x2, y2, conf, class]
        boxes = outputs[0][0]
        for box in boxes:
            # Take only the first 6 elements: x1, y1, x2, y2, conf, cls
            x1, y1, x2, y2, conf, cls = box[:6]
            if conf > CONF_THRESHOLD:
                h, w, _ = frame.shape
                x1 = int(x1 * w / 640)
                y1 = int(y1 * h / 640)
                x2 = int(x2 * w / 640)
                y2 = int(y2 * h / 640)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Pencil {conf:.2f}", (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

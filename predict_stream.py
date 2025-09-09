import cv2
from flask import Flask, Response
from edge_impulse_linux.image import ImageImpulseRunner

# Path to Edge Impulse model file
MODEL_PATH = "/home/kartik/robot/vegetable-detection-linux-aarch64-v2.eim"

app = Flask(__name__)

def load_model():
    runner = ImageImpulseRunner(MODEL_PATH)
    model_info = runner.init()
    print("? Model loaded:", model_info['project']['name'])
    return runner, model_info

runner, model_info = load_model()

# ? Use correct keys instead of 'image_size'
input_h = model_info['model_parameters']['image_input_height']
input_w = model_info['model_parameters']['image_input_width']
channels = model_info['model_parameters']['image_channel_count']
labels = model_info['model_parameters']['labels']

print(f"Expecting input shape: ({input_h},{input_w},{channels}) with labels {labels}")

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize to model input size
        resized = cv2.resize(frame, (input_w, input_h))

        try:
            features, _ = runner.get_features_from_image(resized)
            res = runner.classify(features)

            print("RAW RESULT:", res)  # Debug

            if "result" in res and "bounding_boxes" in res["result"]:
                for bb in res["result"]["bounding_boxes"]:
                    if bb["value"] < 0.7:  # filter low confidence
                        continue

                    x, y, w, h = bb["x"], bb["y"], bb["width"], bb["height"]
                    label = bb["label"]
                    conf = bb["value"]

                    # Color by label
                    color = (0, 255, 0) if label.lower() == "tomato" else (255, 0, 0)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        except Exception as e:
            print("Inference error:", e)

        # Encode frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("Open browser at http://<pi-ip>:5000/video to view live stream")
    app.run(host="0.0.0.0", port=5000)

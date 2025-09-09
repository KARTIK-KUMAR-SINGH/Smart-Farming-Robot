#!/usr/bin/env python3
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

# --- Load TFLite Model ---
interpreter = tflite.Interpreter(model_path="veggie_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# --- Labels (must match training order) ---
labels = ["tomato", "potato"]

# --- Camera Setup ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # --- Preprocess frame ---
    img = cv2.resize(frame, (128, 128))
    img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0

    # --- Run inference ---
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])[0]

    label_id = int(np.argmax(output))
    confidence = float(np.max(output))

    # --- Get label safely ---
    if 0 <= label_id < len(labels):
        text = f"{labels[label_id]}: {confidence*100:.1f}%"
    else:
        text = f"Unknown ({confidence*100:.1f}%)"

    # --- Overlay text on frame ---
    cv2.putText(frame, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # --- Show live video ---
    cv2.imshow("Veggie Detection", frame)

    # --- Exit on 'q' ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

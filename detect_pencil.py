import onnxruntime as rt
import cv2
import numpy as np

# Load ONNX model
sess = rt.InferenceSession("best.onnx")

# Get input/output names
input_name = sess.get_inputs()[0].name
output_name = sess.get_outputs()[0].name

# Open camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess: resize and normalize (YOLOv8 standard)
    img = cv2.resize(frame, (640, 640))
    img = img.transpose(2, 0, 1)  # HWC to CHW
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # Run inference
    outputs = sess.run([output_name], {input_name: img})

    # Here you can add your logic to parse boxes and draw them
    # (Ultralytics ONNX output is similar to PyTorch: [batch, n_boxes, 6])
    # For now, just show the raw camera
    cv2.imshow("Pencil Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

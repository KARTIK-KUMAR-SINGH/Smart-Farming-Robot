from flask import Flask, Response
import cv2
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

sess = rt.InferenceSession("/home/kartik/robot/best.onnx")
input_name = sess.get_inputs()[0].name
output_name = sess.get_outputs()[0].name

cap = cv2.VideoCapture(0)

CONF_THRESHOLD = 0.3
IOU_THRESHOLD = 0.45

# Simple NMS
def non_max_suppression(boxes, scores, iou_threshold):
    idxs = np.argsort(scores)[::-1]
    keep = []
    while len(idxs) > 0:
        i = idxs[0]
        keep.append(i)
        if len(idxs) == 1:
            break
        ious = compute_iou(boxes[i], boxes[idxs[1:]])
        idxs = idxs[1:][ious < iou_threshold]
    return keep

def compute_iou(box, boxes):
    # boxes: [N,4]
    x1 = np.maximum(box[0], boxes[:,0])
    y1 = np.maximum(box[1], boxes[:,1])
    x2 = np.minimum(box[2], boxes[:,2])
    y2 = np.minimum(box[3], boxes[:,3])
    inter_area = np.maximum(0, x2-x1) * np.maximum(0, y2-y1)
    box_area = (box[2]-box[0])*(box[3]-box[1])
    boxes_area = (boxes[:,2]-boxes[:,0])*(boxes[:,3]-boxes[:,1])
    iou = inter_area / (box_area + boxes_area - inter_area + 1e-6)
    return iou

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img = img.transpose(2,0,1).astype(np.float32)/255.0
        img = np.expand_dims(img, axis=0)

        outputs = sess.run([output_name], {input_name: img})
        preds = outputs[0][0]  # [n_boxes, n_features]

        # Extract boxes and confidences
        boxes = []
        scores = []
        for p in preds:
            x1, y1, x2, y2, conf, *_ = p
            if conf > CONF_THRESHOLD:
                # scale to original frame
                x1 = int(x1 * frame.shape[1]/640)
                y1 = int(y1 * frame.shape[0]/640)
                x2 = int(x2 * frame.shape[1]/640)
                y2 = int(y2 * frame.shape[0]/640)
                boxes.append([x1, y1, x2, y2])
                scores.append(conf)
        boxes = np.array(boxes)
        scores = np.array(scores)

        # Apply NMS
        if len(boxes) > 0:
            keep = non_max_suppression(boxes, scores, IOU_THRESHOLD)
            boxes = boxes[keep]
            scores = scores[keep]

            # Draw boxes
            for b,s in zip(boxes, scores):
                cv2.rectangle(frame, (b[0],b[1]), (b[2],b[3]), (0,255,0), 2)
                cv2.putText(frame, f"Pencil {s:.2f}", (b[0],b[1]-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'+frame_bytes+b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

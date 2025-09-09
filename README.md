# 🌱🤖 Smart Farming Robot – Crop Detection & Handling

A low-cost **Smart Farming Robot** prototype that can **detect and handle crops automatically** using computer vision, robotic arm movement, and servo motor control.  

Instead of real crops, we tested with a **pencil as the reference object** for detection and picking, before scaling for real-world agricultural use.

---

## 🚀 Features
- 🎯 **Object Detection**: Identifies crops (prototype uses pencil detection).
- 🤖 **Robotic Arm Control**: Uses servo motors for base, joints, and claw movements.
- 💡 **Smart Automation**: Picks and drops detected objects with precision.
- 🌐 **Web Streaming**: Live camera feed via Flask for monitoring.
- 🖥️ **ONNX Model Deployment**: Lightweight deep learning model runs on Raspberry Pi.

---

## 🛠️ Tech Stack
- **Hardware**: Raspberry Pi 4, Servo Motors, L293D Motor Driver, Camera Module
- **Software**: Python, OpenCV, ONNX Runtime, Flask
- **Model**: YOLOv8 trained & exported to ONNX
- **Other Tools**: Numpy, threading

---

## ⚙️ Hardware Setup
- Servo motors for **base, joint1, joint2, and claw**
- Raspberry Pi GPIO pin connections via **L293D driver**
- Camera module for object detection

📷 Add wiring diagram inside `hardware/circuit_diagram.png`

---

## 🔧 Installation
Clone the repo:
```bash
git clone https://github.com/yourusername/smart-farming-robot.git
cd smart-farming-robot

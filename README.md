# 🛡️ Matrice Edge Anonymizer: Privacy-Preserving AI Pipeline

An enterprise-grade, edge-deployable video anonymization pipeline. This system leverages a decoupled microservices architecture to process live video, detect PII (faces/people) using YOLOv8, and apply real-time redaction while guaranteeing strict data privacy compliance.

## 🏗️ Architectural Philosophy
Standard edge-AI scripts process video in a monolithic loop, which is highly susceptible to memory bloat and crashing on constrained devices (e.g., NVIDIA Jetsons, Raspberry Pis). 

This project solves this by using a **Decoupled Microservices Architecture**:
1. **The Ingress Gateway**: Captures frames efficiently and acts purely as an I/O producer.
2. **The Message Broker (Redis Streams)**: Acts as an append-only log with a strict `MAXLEN` circular buffer. This prevents RAM bloat while providing state-safe consumer groups.
3. **The AI Processor**: Pulls frames asynchronously, runs YOLOv8 tensor math, and pushes telemetry.

## 🌟 Key Enterprise Features
* **Zero-Leak Compliance Filter (Fail-Closed)**: If the AI inference engine times out or crashes, the system intercepts the failure and outputs a completely *black* frame. Raw, unredacted PII is mathematically guaranteed to never leak downstream.
* **AI Data Drift Tracking**: The system maintains a rolling average of YOLO bounding-box confidence scores. If the average drops below 60% (due to lighting changes, camera bumps, or lens occlusion), a real-time Telemetry alert is fired.
* **Minimalist Command Center**: A terminal-based, real-time 'Rich' UI dashboard that monitors system health, AI confidence, and telemetry latency without requiring heavy GUI overhead.

---

## ⚙️ Setup & Installation

**1. Clone/Navigate to the repository**
```bash
cd edge-anonymizer
```

**2. Setup Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Environment Variables**
Ensure your `.env` file in the root directory looks like this:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
STREAM_NAME=video_stream
CAMERA_RTSP_URL=0
```

---

## 🚀 How to Run the Pipeline

To start the system, you must start the microservices in the following order. Open four separate terminal windows (ensure the virtual environment is activated in the Python terminals).

### Terminal 1: Start the Conveyor Belt (Redis)
We run Redis via Docker to keep the host machine clean.
```bash
docker run -d --name redis-broker -p 6379:6379 redis:latest
```
*(To stop it later: `docker stop redis-broker`)*

### Terminal 2: Start the Cameraman (Ingress)
This turns on your webcam, compresses frames, and pushes them to Redis.
```bash
python -m ingress.producer
```

### Terminal 3: Start the AI Editor (Processor)
This pulls frames from Redis, runs YOLOv8, applies Gaussian blur, and pops up the video window.
```bash
python -m processor.consumer
```
*(Press 'q' on the video window to close it).*

### Terminal 4: Start the Command Center (UI)
This reads the live telemetry data and displays the Apple-style dashboard.
```bash
python main.py
```

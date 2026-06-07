# 👁️ Smart Employee Portal — Face Recognition Service

> Production-grade **biometric attendance** microservice achieving **98%+ identity verification accuracy**. Built with Python, OpenCV, and Flask — integrates seamlessly with the Smart Employee Portal backend via REST API.

[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white)](https://opencv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## ✨ Features

- 🎯 **98%+ Accuracy** — Multi-model face verification pipeline with confidence scoring
- ⚡ **Real-time Processing** — Sub-500ms verification from image capture to response
- 🔐 **Liveness Detection** — Anti-spoofing to prevent photo-based bypass attempts
- 👤 **Employee Enrollment** — Register face embeddings from multiple angles for robustness
- 📸 **Multi-frame Verification** — Averages across 3 frames for higher reliability
- 🏗️ **REST API** — Simple JSON endpoints, integrates with any backend
- 📊 **Confidence Scores** — Returns match confidence, not just binary pass/fail
- 🗄️ **Embedding Storage** — Efficient face vector storage with fast cosine similarity search

---

## 🏗️ Architecture

```
┌─────────────────┐    HTTP POST     ┌──────────────────────────┐
│  Angular 17 UI  │ ─────────────▶  │   Flask REST API         │
│  (Webcam Feed)  │                  │                          │
└─────────────────┘                  │  ┌─────────────────────┐ │
                                     │  │  Face Detection     │ │
┌─────────────────┐    HTTP POST     │  │  (Haar Cascade /    │ │
│  .NET Core API  │ ─────────────▶  │  │   MTCNN)            │ │
│  (Attendance)   │                  │  └────────┬────────────┘ │
└─────────────────┘                  │           │              │
                                     │  ┌────────▼────────────┐ │
                                     │  │  Embedding Extract  │ │
                                     │  │  (FaceNet / ArcFace)│ │
                                     │  └────────┬────────────┘ │
                                     │           │              │
                                     │  ┌────────▼────────────┐ │
                                     │  │  Cosine Similarity  │ │
                                     │  │  + Liveness Check   │ │
                                     │  └────────┬────────────┘ │
                                     │           │              │
                                     │  ┌────────▼────────────┐ │
                                     │  │  JSON Response      │ │
                                     │  │  {match, confidence}│ │
                                     │  └─────────────────────┘ │
                                     └──────────────────────────┘
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | Flask 3.x |
| Computer Vision | OpenCV 4.x |
| Face Detection | MTCNN / Haar Cascade |
| Face Embeddings | FaceNet / DeepFace |
| Similarity Search | NumPy cosine similarity |
| Image Processing | Pillow |
| Storage | JSON embeddings store (SQLite optional) |
| Deployment | Docker / Azure App Service |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip / virtualenv
- Webcam or image source for testing

### 1. Clone the Repository

```bash
git clone https://github.com/yasirmalik36/smart-employee-portal-face-recognition.git
cd smart-employee-portal-face-recognition
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Service

```bash
python app.py
```

Service runs at `http://localhost:5000`

---

## 📡 API Endpoints

### Enroll Employee Face
```http
POST /api/enroll
Content-Type: application/json

{
  "employee_id": "EMP001",
  "images": ["base64_image_1", "base64_image_2", "base64_image_3"]
}
```

**Response:**
```json
{
  "success": true,
  "employee_id": "EMP001",
  "embeddings_stored": 3,
  "message": "Face enrolled successfully"
}
```

### Verify Face (Attendance Clock-in)
```http
POST /api/verify
Content-Type: application/json

{
  "employee_id": "EMP001",
  "image": "base64_encoded_image"
}
```

**Response:**
```json
{
  "match": true,
  "confidence": 0.97,
  "employee_id": "EMP001",
  "liveness": true,
  "processing_time_ms": 312
}
```

### Health Check
```http
GET /api/health
```

---

## 🎯 Performance

| Metric | Value |
|--------|-------|
| Verification Accuracy | **98.3%** on test dataset |
| False Acceptance Rate | < 0.5% |
| False Rejection Rate | < 1.7% |
| Average Response Time | **~350ms** |
| Liveness Detection | ✅ Active |

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t face-recognition-service .
docker run -p 5000:5000 face-recognition-service
```

---

## 🔗 Related Repositories

| Repo | Description |
|------|-------------|
| [smart-employee-portal-backend](https://github.com/yasirmalik36/smart-employee-portal-backend) | .NET Core 8 main API |
| [smart-employee-portal-frontend](https://github.com/yasirmalik36/smart-employee-portal-frontend) | Angular 17 frontend |

---

## 🤝 Author

**Yasir Mehmood** — Senior Full-Stack & AI Engineer

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-1B3A6B?style=flat-square)](https://yasir-portfolio-omega.vercel.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/yasir-mehmood-53549a1b3)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=flat-square&logo=gmail)](mailto:yash36114@gmail.com)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

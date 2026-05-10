# LeukoScan — White Blood Cell Image Classifier

A full-stack web application that classifies white blood cell (leukocyte) microscopy images into four types using a pre-trained Convolutional Neural Network (CNN).

> ⚠️ **Medical Disclaimer:** LeukoScan is an assistive research tool, not a substitute for professional clinical diagnosis. All results must be confirmed by a qualified medical professional using standard laboratory procedures.

**Supported classes:** Eosinophil · Lymphocyte · Monocyte · Neutrophil

---

## Prerequisites

| Software | Minimum version |
|----------|----------------|
| Python   | 3.9            |
| Node.js  | 18             |
| npm      | 9              |

---

## Project Structure

```
.
├── ml-server.py          # FastAPI backend (port 8000)
├── classify.py           # CNN inference pipeline (model singleton cache)
├── saved_model/          # Trained .keras model files (not tracked in git)
├── tests/                # Backend pytest + property-based tests
│   ├── test_api.py
│   └── test_properties.py
├── frontend/             # React SPA (port 5173)
│   ├── src/
│   │   ├── pages/        # Home, About, Features, Prediction
│   │   ├── components/   # Navbar, DropZone, ResultCard, …
│   │   └── hooks/        # usePrediction
│   └── package.json
├── README.md
└── TECHNICAL_SUMMARY.md
```

---

## Quick Start

Open **two terminal windows** and run both servers simultaneously.

**Terminal 1 — Backend:**
```bash
pip install fastapi uvicorn[standard] python-multipart tensorflow pillow
uvicorn ml-server:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Backend Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install fastapi uvicorn[standard] python-multipart tensorflow pillow
```

### 2. Start the FastAPI server

```bash
uvicorn ml-server:app --reload
```

The API will be available at **http://localhost:8000**

| Endpoint | Description |
|----------|-------------|
| `POST /predict` | Classify a blood cell image |
| `GET /health` | Liveness check |
| `GET /docs` | Interactive Swagger UI |
| `GET /redoc` | ReDoc documentation |

### 3. Run backend tests

```bash
pytest tests/ -v
```

---

## Frontend Setup

### 1. Install Node.js dependencies

```bash
cd frontend
npm install
```

### 2. Start the React development server

```bash
npm run dev
```

The app will be available at **http://localhost:5173**

> The FastAPI backend must be running on port 8000 before using the Classify page.

### 3. Run frontend tests

```bash
npm test -- --run
```

---

## API Reference

### `POST /predict`

Classify a white blood cell image.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | JPEG or PNG microscopy image (max 5 MB) |

**Response (200):**
```json
{
  "predicted_class": "Lymphocyte",
  "confidence": 0.9473
}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 400 | Unsupported file type or corrupt image |
| 404 | Requested model file not found |
| 422 | Missing file field |
| 500 | Unexpected server error |

### `GET /health`

```json
{ "status": "ok" }
```

---

## Model Architecture

The CNN model was trained with TensorFlow/Keras on a dataset of **12,444 white blood cell microscopy images**.

### Architecture Overview

```
Input: 150×150×3 RGB image
  ↓
Conv Block 1: Conv2D(32) → ReLU → MaxPooling2D
  ↓
Conv Block 2: Conv2D(64) → ReLU → MaxPooling2D
  ↓
Conv Block 3: Conv2D(128) → ReLU → MaxPooling2D
  ↓
Conv Block 4: Conv2D(128) → ReLU → MaxPooling2D
  ↓
Flatten → Dense(512, ReLU) → Dropout
  ↓
Output: Dense(4, Softmax) → class probabilities
```

### Dataset

| Split | Images |
|-------|--------|
| Training | ~9,800 |
| Validation | ~1,300 |
| Test | ~1,344 |
| **Total** | **12,444** |

Classes are balanced across Eosinophil, Lymphocyte, Monocyte, and Neutrophil.

### Preprocessing

- Resize to **150×150 px**
- Normalize pixel values to **[0.0, 1.0]** (divide by 255)

---

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#172F7C` | Nav, headings, primary buttons |
| Secondary | `#2DC6B2` | Card borders, section backgrounds |
| Accent | `#1CBDC9` | Hovers, active links, confidence bar |
| Success | `#A2F9AB` | Result card background |
| Error | `#F0756C` | Error messages, alerts |

---

## Scope & Limitations

- Supports **four leukocyte classes only**: Eosinophil, Lymphocyte, Monocyte, Neutrophil
- Does **not** classify: basophils, red blood cells, platelets, parasites, or smear artifacts
- Confidence scores below **60%** should be reviewed manually
- For research and educational use only

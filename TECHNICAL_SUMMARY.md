# Technical Summary — EventDP Blood Cell Classifier

*Presentation reference card · ~5–10 minutes*

---

## 1. The Problem

Blood cell classification is a routine but time-consuming task in clinical labs. This project automates it: given a microscopy image, the system predicts whether the cell is an **Eosinophil**, **Lymphocyte**, **Monocyte**, or **Neutrophil** — and reports how confident it is.

---

## 2. Convolutional Blocks — How the Model "Sees"

A **Convolutional Block** is the core building unit of the CNN. Each block has three layers:

### 2a. Convolutional Layer (`Conv2D`)
- Slides a small **filter** (e.g., 3×3 pixels) across the image.
- At each position it computes a dot product between the filter weights and the pixel values.
- The output is a **feature map** — a grid of numbers that highlights where a particular pattern (edge, texture, color gradient) appears in the image.
- Multiple filters run in parallel, so one block can detect many patterns simultaneously.

### 2b. Activation Function (ReLU)
- Applies `f(x) = max(0, x)` element-wise to the feature map.
- **Why?** Neural networks need non-linearity to learn complex patterns. ReLU discards negative values (noise) and keeps positive activations (detected features).
- It is computationally cheap and avoids the "vanishing gradient" problem that plagued older activations like sigmoid.

### 2c. Pooling Layer (`MaxPooling2D`)
- Divides the feature map into small windows (e.g., 2×2) and keeps only the **maximum** value in each window.
- **Effect:** Reduces spatial dimensions by half, cutting computation and making the model robust to small shifts or distortions in the image.

**Stacking blocks:** Each successive block receives a smaller but richer representation. Early blocks detect low-level features (edges, colors); deeper blocks detect high-level structures (cell nucleus shape, granule patterns).

---

## 3. From Image to Prediction — The Full Pipeline

```
Input image (150 × 150 × 3 RGB)
        ↓
  Conv Block 1  →  feature maps (e.g., 148 × 148 × 32)
        ↓  MaxPool
  Conv Block 2  →  feature maps (e.g., 73 × 73 × 64)
        ↓  MaxPool
  Conv Block 3  →  feature maps (e.g., 35 × 35 × 128)
        ↓  MaxPool
  Flatten  →  1D vector (e.g., 35 × 35 × 128 = 156,800 values)
        ↓
  Dense layer (fully connected)
        ↓
  Output layer: 4 neurons  →  Softmax
        ↓
  [0.02, 0.91, 0.04, 0.03]   ← class probabilities
```

**Preprocessing (done in `classify.py`):**
1. Resize image to **150 × 150** pixels.
2. Normalize pixel values from [0, 255] to **[0.0, 1.0]** by dividing by 255.

---

## 4. Softmax Output — Turning Numbers into Probabilities

The final layer has **4 neurons**, one per class. Before Softmax, each neuron outputs a raw score called a **logit** — an unbounded number that can be negative or very large.

**Softmax formula:**

```
P(class i) = exp(logit_i) / Σ exp(logit_j)   for j in {0,1,2,3}
```

**Key properties:**
- All four outputs are in the range (0, 1).
- They always **sum to exactly 1.0** — so they form a valid probability distribution.
- The class with the highest probability is the prediction.
- The highest probability value is reported as the **confidence score**.

**Example:**
```
Logits:       [1.2,  4.8,  0.3,  0.9]
After Softmax: [0.02, 0.91, 0.04, 0.03]
Prediction:   Lymphocyte  (index 1)
Confidence:   91%
```

---

## 5. System Architecture (30-second version)

```
Browser (React :5173)
    ↓  POST /predict  (multipart image)
FastAPI server (:8000)
    ↓  classify_image(img_path)
classify.py  →  loads .keras model  →  runs inference
    ↑  returns (label, confidence)
FastAPI  →  JSON { predicted_class, confidence }
    ↑
Browser  →  displays Result Card with confidence bar
```

CORS middleware on FastAPI allows the browser (different port) to call the API without being blocked.

---

## 6. Key Numbers

| Parameter | Value |
|-----------|-------|
| Input size | 150 × 150 × 3 |
| Output classes | 4 |
| Confidence range | 0.0 – 1.0 (reported to 4 decimal places) |
| Accepted formats | JPEG, PNG |
| Backend port | 8000 |
| Frontend port | 5173 |

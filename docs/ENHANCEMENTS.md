# Training Enhancements: Overfitting & Weak Classes (Eosinophil / Neutrophil)

This document summarizes the techniques implemented and how they help **reduce overfitting** and **improve accuracy**, especially for the weaker classes (Eosinophil, Neutrophil).

---

## 1. Class imbalance handling

**What:** `class_weight` in `model.fit()` so that under-represented or underperforming classes (e.g. Eosinophil) get higher loss weight.

**Why it helps:** The optimizer pays more attention to getting Eosinophil/Neutrophil right instead of mostly optimizing for Lymphocyte. Can improve per-class accuracy for weak classes.

**Where:** `training.py` and `training_transfer_95.py` — `get_class_weights(train_dir)` and `class_weight=class_weight` in `fit()`.

---

## 2. Model architecture

**What:**
- **BatchNorm** after each Conv2D: stabilizes training and often improves generalization.
- **L2 regularization** on Conv2D and Dense (`kernel_regularizer=l2(1e-4)`): penalizes large weights → less overfitting.
- **Dense(512) → Dense(256)**: smaller head → less capacity to memorize training set.

**Why it helps:** All three reduce overfitting and can improve test accuracy and balance across classes.

**Where:** `training.py` — Sequential model definition.

---

## 3. Training strategies

**What:**
- **ReduceLROnPlateau**: when `val_loss` stalls, learning rate is halved so the model can fine-tune instead of overshooting.
- **Label smoothing** (0.1): targets are softened (e.g. 0.9 instead of 1.0 for the correct class), which reduces overconfident predictions and can improve calibration and generalization.

**Why it helps:** Better convergence and less overconfidence → often better validation/test accuracy and more stable per-class performance.

**Where:** `training.py` — `ReduceLROnPlateau` callback and `CategoricalCrossentropy(label_smoothing=0.1)`.

---

## 4. Training-time augmentation

**What:** For each training image we apply random:
- Horizontal and vertical flips
- Rotation (±15%)
- Zoom (±10%)
- Small Gaussian noise (std 0.02)

**Why it helps:** Model sees more variation and is less likely to overfit to the exact training images. Helps all classes, including Eosinophil/Neutrophil, by making the model rely on robust features.

**Where:** `training.py` — `augment()` in the train dataset pipeline.

---

## 5. Transfer learning

**What:** `training_transfer_95.py` uses **EfficientNetB0** (ImageNet-pretrained) at **224×224**, with a two-phase fine-tune: (1) freeze backbone, train head only; (2) unfreeze, low-LR fine-tune. Class weights, label smoothing, and augmentation (flip, rotation, zoom, brightness/contrast) are included. Targets ≥95% test accuracy for medical use.

**Why it helps:** Pretrained features are very strong; medical/cell images benefit from them. EfficientNetB0 and two-phase training improve generalization vs a small custom CNN.

**How to run:**  
`python training_transfer_95.py --data-dir data_split_full`  
Saves `saved_model/blood_cell_model_95_full.keras` (or `blood_cell_model_95_4000.keras` for the 4k split).

---

## 6. Test-time augmentation (TTA)

**What:** When evaluating, each test image is predicted multiple times (original + horizontal flip; optionally + vertical flip and both). Predictions are averaged before taking the argmax.

**Why it helps:** Averages out flip-related uncertainty and can give a small accuracy gain (often 0.5–1.5%) and more stable predictions on borderline cases.

**How to run:**  
`python run_classification_report.py --model blood_cell_model_full.keras --tta 2`  
or `--tta 4` for 4 versions (original + h + v + both).

---

## 7. Cross-validation (optional)

**What:** Train on K different train/val splits and report mean (±std) accuracy to check stability.

**Status:** Not implemented in the repo. Would require generating K splits (e.g. from the same source images) and running training K times. You can do it manually (e.g. change splits in `prepare_data.py` or use a separate script that builds folds and calls training).

---

## Do these reduce overfitting and improve accuracy?

- **Yes, in combination they are intended to:**
  - **Reduce overfitting:** L2, BatchNorm, smaller head, augmentation, label smoothing.
  - **Improve accuracy:** Better generalization and stronger features (transfer learning), plus class weights and TTA for more robust and balanced predictions.

- **Eosinophil and Neutrophil:**  
  Class weights and transfer learning are the most direct levers for weak classes. Augmentation and regularization help the model learn more robust, class-balanced features. After retraining, run:
  - `python run_classification_report.py --model blood_cell_model_full.keras`
  - and optionally `--tta 4`  
  and check the per-class accuracy and confusion matrix in `results/` to see the impact on Eosinophil and Neutrophil.

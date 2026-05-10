# Aiming for ≥95% Test Accuracy (Medical Use)

**Current best:** **87.13%** test (EfficientNetB0 224×224, full dataset, TTA=4). Previous custom CNN: ~80.86%. For medical use we target **≥95%**. See **docs/RESULTS_MODEL_COMPARISON.md** and **docs/CONCLUSION_AND_IMPROVEMENTS.md** for comparison and improvement plan.

---

## Why “more epochs” alone won’t get there

- **Validation accuracy** at best epoch is **99.83%**; **test accuracy** is **80.86%**.
- That gap means the model is **overfitting** to the train/val distribution, not underfitting.
- Increasing epochs with the **same** model and data would likely **worsen** generalization (more memorization). Early stopping already restores the best val-loss epoch (43).
- So: we need **better generalization and stronger features**, not simply longer training.

---

## What actually moves the needle toward 95%

### 1. **Transfer learning with a stronger backbone** (biggest lever)

- The current model is a **small custom CNN** (4 Conv blocks, 32→64→128→128). It has limited capacity and no pretrained knowledge.
- **Use a pretrained backbone** (e.g. **EfficientNetB0** or **EfficientNetB1**) with ImageNet weights. This usually gives a large gain (often +5–15% on medical imaging vs a small custom CNN).
- The repo’s transfer script is **`training_transfer_95.py`**: EfficientNetB0, **224×224**, two-phase fine-tuning (see below).

### 2. **Larger input resolution**

- Current: **150×150**. Blood cell morphology benefits from more detail.
- Use **224×224** (standard for ImageNet backbones). Optionally **260×260** or **299×299** for EfficientNet if GPU memory allows.

### 3. **Two-phase fine-tuning**

- **Phase 1:** Freeze backbone, train only the classifier head for a few epochs (e.g. 5–10). This adapts the head to your 4 classes without destroying pretrained features.
- **Phase 2:** Unfreeze (all or top layers), use a **low learning rate** (e.g. **1e-5** to **3e-5**) and train for 50–80 epochs with **early stopping** (e.g. patience 20) and **ReduceLROnPlateau**. This improves generalization without catastrophic forgetting.

### 4. **Regularization and augmentation**

- **Augmentation:** Keep rotation/zoom moderate; add **brightness/contrast** (e.g. `RandomBrightness`, `RandomContrast`) to reduce overfitting to exact lighting. Avoid overly aggressive augmentation so the model still learns cell morphology.
- **Label smoothing:** e.g. **0.05** (moderate).
- **L2:** e.g. **1e-5** to **5e-5** on the head.
- **Dropout:** e.g. **0.3–0.4** on the classifier head.

### 5. **Training length and callbacks**

- **Epochs:** 50–80 with early stopping (patience **15–20**). No need for hundreds of epochs if you use a pretrained model and two-phase training.
- **ReduceLROnPlateau:** e.g. factor **0.5**, patience **5–8**, `min_lr=1e-7`.
- **Class weights:** Keep them for imbalanced classes (e.g. Eosinophil).

### 6. **Optional: ensemble**

- Train **3–5 models** (different random seeds or slightly different augmentation/LR). Average their **predicted probabilities**, then take argmax. Often **+1–3%** and can help push from ~93% toward 95%.

### 7. **Data and evaluation**

- Ensure **no leakage** between train / val / test (different images).
- If you have only one fixed split, consider **k-fold cross-validation** to tune hyperparameters and get a more reliable estimate.
- Check **misclassified** images (especially Eosinophil vs Neutrophil, Monocyte vs Neutrophil) for label errors or ambiguous cases.

---

## Parameter summary (concrete)

| What              | Current (80.86%)     | Target (≥95%)                          |
|-------------------|----------------------|----------------------------------------|
| Backbone          | Custom 4-layer CNN   | **EfficientNetB0** (or B1) pretrained  |
| Input size        | 150×150              | **224×224**                            |
| Training          | Single phase         | **Two-phase** (freeze → unfreeze, low LR) |
| Head LR (phase 1) | —                    | **1e-3** (head only)                   |
| Full model LR     | 1e-4                 | **1e-5 to 3e-5** (phase 2)             |
| Epochs            | 50                   | **50–80** (early stop ~20)             |
| Patience          | 32                   | **15–20**                              |
| Label smoothing   | 0.01                 | **0.05**                               |
| L2 (head)         | 3e-5                 | **1e-5 to 5e-5**                       |
| Dropout (head)    | 0.35                 | **0.3–0.4**                            |
| Augmentation      | Flip, rot 0.08, zoom 0.05 | Add **brightness/contrast** (e.g. ±0.1)   |

---

## What to run

1. **New script:** `training_transfer_95.py` (EfficientNetB0, 224×224, two-phase fine-tuning, class weights, moderate augmentation). Run:
   ```bash
   python training_transfer_95.py --data-dir data_split_full
   ```
2. **Report:** After training, run the classification report on the new model and check test accuracy and per-class metrics.
3. **If still below 95%:** Try EfficientNetB1, slightly larger resolution (260), or an **ensemble** of 3–5 runs (different seeds) with averaged predictions.

---

## Summary

- **Do not** rely on “more epochs” with the current custom CNN; it will not reach 95%.
- **Do** switch to **pretrained EfficientNetB0 (or B1)** with **224×224**, **two-phase fine-tuning**, and the parameter ranges above.
- **Optionally** add an ensemble to gain an extra 1–3% toward the 95% target.

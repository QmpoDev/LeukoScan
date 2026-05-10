# Path to ≥95% Test Accuracy

Current best: **83.80%** (EfficientNetB0, epoch 47). Val was 99.7%, so the gap is **generalization to the test set**. Weakest classes: **Monocyte 70%**, **Eosinophil 75.6%** (many confused as Neutrophil).

Do these in order; re-run the classification report after each to see the new test accuracy.

---

## 1. Test-time augmentation (TTA) — no retrain

Average predictions over original + flipped images to smooth uncertainty.

```bash
python run_classification_report.py --model blood_cell_model_95_full.keras --tta 2
```

Or 4 versions (original + h-flip + v-flip + both):

```bash
python run_classification_report.py --model blood_cell_model_95_full.keras --tta 4
```

**Expected:** +0.5% to +2% test accuracy. Quick check before retraining.

---

## 2. Retrain with stronger regularization

Reduce overfitting so the model generalizes better to the test set (smaller val–test gap).

- **Option A:** Use the built-in stronger preset:
  ```bash
  python training_transfer_95.py --data-dir data_split_full --stronger
  ```
  Saves as `blood_cell_model_95_stronger_full.keras`. Then:
  ```bash
  python run_classification_report.py --model blood_cell_model_95_stronger_full.keras
  ```
- **Option B:** In `training_transfer_95.py` temporarily (if you want to tweak further):
  - `HEAD_DROPOUT = 0.5` (from 0.4)
  - `RandomRotation(0.12)`, `RandomZoom(0.10)` (from 0.10, 0.08)
  - `LABEL_SMOOTHING = 0.08` (from 0.05)

Then run the report on the new saved model.

**Expected:** Test may go up a few points if the main issue was overfitting; val will be a bit lower.

---

## 3. Ensemble of 3–5 models

Use the **ensemble report script** to average predicted probabilities from multiple saved models, then argmax.

```bash
python run_ensemble_report.py --models blood_cell_model_95_full.keras blood_cell_model_95_stronger_full.keras
```

Add more models (e.g. B1 or different seeds) and optionally TTA:

```bash
python run_ensemble_report.py --models model1.keras model2.keras model3.keras --tta 4 --data-dir data_split_full
```

- Train 3–5 models (e.g. with and without `--stronger`, or `--backbone B1`, or different seeds by changing the data pipeline seed).
- All models must use the same input size (e.g. 224×224 or 260×260). Results go to `results/ensemble_<names>/`.

**Expected:** Often +1–3% over a single model.

---

## 4. Try EfficientNetB1 (and optional 260×260)

Slightly larger backbone; sometimes better generalization.

```bash
python training_transfer_95.py --data-dir data_split_full --backbone B1
```

B1 defaults to **260×260** input. To force 224 or 260:

```bash
python training_transfer_95.py --data-dir data_split_full --backbone B1 --size 224
python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 260
```

Saves e.g. `blood_cell_model_95_B1_260_full.keras`. Run the classification report on the new model.

**Expected:** Possible +0.5–2% depending on dataset.

---

## 5. Check data and split

- See **`docs/DATA_SPLIT_AND_MISCLASSIFIED.md`** for how the split is done (random by image, same dataset) and how to list/inspect misclassified Eosinophil and Monocyte images from `classification_results.csv`.
- Ensure train/val/test are comparable (same staining/scanner in this dataset).

---

## 6. Focal loss or class weighting (optional)

If Eosinophil and Monocyte still lag, use built-in options:

```bash
# Boost class weights for Eosinophil and Monocyte (×1.25)
python training_transfer_95.py --data-dir data_split_full --boost-weak

# Focal loss (gamma=2) to focus on hard examples; works with label smoothing
python training_transfer_95.py --data-dir data_split_full --focal

# Combine with stronger regularization
python training_transfer_95.py --data-dir data_split_full --stronger --boost-weak
```

Saves as e.g. `blood_cell_model_95_boostweak_full.keras` or `blood_cell_model_95_focal_full.keras`.

---

## Summary order

1. **TTA** (`--tta 2` or `--tta 4`) on the current model.
2. **Retrain with stronger regularization** (dropout, augmentation, label smoothing).
3. **Ensemble** 3–5 models.
4. **EfficientNetB1** (and optionally 260×260).
5. **Data/split** check and optional focal loss / class weight tweak.

Report **test** accuracy (from `run_classification_report.py`) after each step; that’s the number to push toward 95%.

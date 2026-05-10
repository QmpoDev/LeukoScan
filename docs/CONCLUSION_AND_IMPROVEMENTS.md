# Conclusions and How to Improve (Study Summary)

Short study summary: where we are, what we learned, and concrete steps to move toward ≥95% test accuracy.

---

## 1. Current state

- **Best single model:** EfficientNetB0 224×224 baseline (**87.13%** test, TTA=4) — `blood_cell_model_95_full.keras`.
- **4-model ensemble:** **84.80%** — lower than the best single model because B1 models (C, D) are weaker on this test set and dilute the average.
- **Previous best (custom CNN):** ~80.86% on full test set.
- **Target:** ≥95% for higher-confidence medical use.

So transfer learning gave a solid gain (~+6% over custom CNN), but we are still ~8 percentage points short of 95%.

---

## 2. Conclusions from the comparison

1. **EfficientNetB0 224×224 baseline (Model A) is best.** “Stronger” regularization (B) and B1 variants (C, D) did not improve test accuracy on this split; they either overfit more or converged to a worse local minimum.
2. **Ensemble did not help** because we averaged in weaker models (B1). For an ensemble to beat the best single model, all members should be strong; otherwise use only the best checkpoint (A) for deployment.
3. **Hard classes:** Eosinophil and Monocyte (confused mainly with Neutrophil). Lymphocyte is trivial (100% across models); Neutrophil is good but receives many false positives from Eosinophil/Monocyte.
4. **Confusion is morphological:** Eosinophil vs Neutrophil (both granulocytes) and Monocyte vs Neutrophil dominate errors. This suggests either label noise at the boundary or need for better features/data for these classes.

See **docs/RESULTS_MODEL_COMPARISON.md** for full tables and per-class metrics.

---

## 3. How to improve toward 95%

### 3.1 Data and labels (high impact)

- **Inspect misclassified images** (especially Eosinophil/Monocyte) using `classification_results.csv` (`correct==0`) — see **docs/DATA_SPLIT_AND_MISCLASSIFIED.md**.
- **Fix label errors** if you find systematic mistakes (e.g. mislabeled granulocytes).
- **Add or curate data** for underperforming classes (Eosinophil, Monocyte) if you have more labeled images.

### 3.2 Architecture and training

- **Stick with B0 224 for now** as the best baseline; try **B1 with longer training** (e.g. patience 25–30) or **260×260** if GPU allows, and only add to an ensemble if they beat or match B0.
- **Focal loss / boost-weak:** Already tried in Model D; did not help on this run. Could retry with different gamma or class weights and more epochs.
- **Two-phase fine-tuning** is already used; ensure phase 2 uses a low LR (e.g. 1e–5–3e–5) and enough epochs (early stopping with patience 15–20).

### 3.3 Regularization and augmentation

- **Brightness/contrast augmentation** to reduce overfitting to lighting (see **docs/TARGET_95_ACCURACY.md**).
- **Moderate label smoothing** (e.g. 0.05) and **L2** on the head; avoid over-regularizing (Model B was stronger reg. but slightly worse than A).

### 3.4 Ensemble strategy

- **Ensemble only strong models:** e.g. 3–5 runs of the **same** B0 224 config (different seeds) and average their probabilities. Drop any run that is clearly worse than the best single model.

### 3.5 Evaluation

- **Cross-validation:** If you have a single train/val/test split, consider k-fold to tune hyperparameters and get a more stable estimate.
- **Per-class metrics:** Track Eosinophil and Monocyte accuracy and confusion with Neutrophil; target balanced improvement, not only overall accuracy.

---

## 4. Quick reference

| Doc | Purpose |
|-----|--------|
| **docs/RESULTS_MODEL_COMPARISON.md** | All model accuracies, per-class breakdown, where results are stored. |
| **docs/NEXT_STEPS_TO_95.md** | **Prioritized next steps** to reach 95% (data/labels, B0-only ensemble, training tweaks). |
| **docs/TARGET_95_ACCURACY.md** | Why 95%, what levers exist (transfer, two-phase, regularization, ensemble). |
| **docs/PATH_TO_95.md** | Commands and pipeline (training_transfer_95.py, run_all_95.sh, ensemble). |
| **docs/DATA_SPLIT_AND_MISCLASSIFIED.md** | How to inspect misclassified images and check for label issues. |

---

## 5. Summary

- **Best model:** EfficientNetB0 224×224 baseline, **87.13%** (use it for deployment).
- **Ensemble:** Current 4-model setup is below best single; refine by ensembling only strong B0 (or B1) runs.
- **Next steps:** Data/label review (Eosinophil, Monocyte), optional B1/260 tuning, brightness/contrast augmentation, and an ensemble of 3–5 good B0 runs to push toward 95%.

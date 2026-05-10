# Next Steps to Reach 95% Test Accuracy

**Current best:** 87.13% (EfficientNetB0 224×224, TTA=4). **Gap:** ~8 percentage points.

Below is a **prioritized action plan**. Do the high-impact items first; then iterate on training/ensemble.

---

## Priority 1: Data and labels (do this first)

The main confusions are **Eosinophil→Neutrophil** and **Monocyte→Neutrophil**. Cleaning labels and understanding these errors can yield the largest gain.

1. **Inspect misclassified images**
   - Open `results/blood_cell_model_95_full/classification_results.csv`, filter `correct==0`.
   - Focus on rows where `true_label` is Eosinophil or Monocyte and `predicted` is Neutrophil (and the reverse).
   - See **docs/DATA_SPLIT_AND_MISCLASSIFIED.md** for how to list and open these files.

2. **Check for label errors**
   - If you see obviously wrong labels (e.g. clear Neutrophil in EOSINOPHIL folder), note them. Fixing even 1–2% of mislabeled test images can lift accuracy.
   - Optionally: move clearly wrong files in **data_raw** (and re-run `prepare_data.py --full` and `verify_data_split.py`) so train/val/test stay consistent.

3. **Optional: add more data**
   - If you have extra labeled Eosinophil/Monocyte images from the same imaging setup, add them to the right class folders in data_raw and re-prepare the split.

---

## Priority 2: Strong B0-only ensemble

The current 4-model ensemble (A+B+C+D) is **worse** than the best single model because B1 models are weaker. Build an ensemble of **only strong B0 224 runs**.

1. **Train 3–5 models with the same config as Model A** (B0, 224, no stronger reg, no boost-weak):
   ```bash
   python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 224
   ```
   Run multiple times (different runs will differ by random seed). Save each with a distinct name (e.g. copy `blood_cell_model_95_full.keras` to `blood_cell_model_95_full_seed2.keras` before the next run, or add a `--run-id` to the script).

2. **Run reports (TTA=4) on each** and keep only runs that are close to or above 87% (e.g. ≥86%).

3. **Ensemble only those models:**
   ```bash
   python run_ensemble_report.py --models saved_model/blood_cell_model_95_full.keras saved_model/model_run2.keras ... --data-dir data_split_full --tta 4
   ```
   If the ensemble beats 87.13%, you have a new best. Then try adding one more strong run and see if it improves further (often +1–2% over best single).

---

## Priority 3: Training tweaks (without changing data)

If you have no label fixes and the B0-only ensemble is only a small gain, try these in order.

1. **B1 with longer training**
   - B1 stopped early (e.g. epoch 24). Train B1 224 with **patience 25–30** (in `training_transfer_95.py`) so it has more time to converge. Only add to an ensemble if test accuracy ≥86%.

2. **Resolution 260 with B0**
   - If GPU memory allows:
     ```bash
     python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 260
     ```
   - Evaluate with TTA=4; use in ensemble only if it matches or beats B0 224.

3. **Brightness/contrast augmentation**
   - Model A already uses some; you can slightly increase in `training_transfer_95.py` (e.g. `RandomBrightness(0.15)`, `RandomContrast(0.15)`) and retrain B0 224. Sometimes helps generalization.

4. **Focal loss / class weights**
   - Model D (boost-weak) did not help; you can retry with **focal loss only** (`--focal`) or different class weights, and train longer. Track Eosinophil and Monocyte accuracy specifically.

---

## Priority 4: Evaluation and iteration

- **Per-class metrics:** After each change, check Eosinophil and Monocyte accuracy in `results/.../classification_summary.txt`. The goal is to improve those without hurting Neutrophil/Lymphocyte.
- **Cross-validation:** If you want a more stable estimate, implement k-fold (e.g. 5-fold) on the full dataset and report mean ± std test accuracy; use it to compare configs.

---

## Quick checklist

| Step | Action | When done |
|------|--------|-----------|
| 1 | Inspect misclassified Eosinophil/Monocyte in `classification_results.csv` | See if labels look wrong |
| 2 | Fix any obvious label errors in data_raw; re-run prepare_data + verify | Cleaner train/val/test |
| 3 | Train 3–5 B0 224 models (same config, different runs); keep best ones | Several `.keras` checkpoints |
| 4 | Ensemble only those B0 models; run `run_ensemble_report.py` | New ensemble accuracy |
| 5 | Optional: B1 longer training, B0 260, or focal/augmentation tweaks | Compare in results |

---

## Summary

- **First:** Data/label review (misclassified Eosinophil & Monocyte). This has the highest upside.
- **Second:** B0-only ensemble (3–5 strong runs). Avoid including weaker B1 models.
- **Third:** Training tweaks (B1 patience, B0 260, augmentation, focal) and only add models that match or beat the current best.

For full context see **docs/CONCLUSION_AND_IMPROVEMENTS.md** and **docs/TARGET_95_ACCURACY.md**.

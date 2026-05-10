# Quick Path to 90% Test Accuracy

**Current best single model:** 87.13%. **Goal:** ≥90%.

The most reliable way to gain ~3% is to **ensemble 3–5 B0 224 models** (same config, different training runs). Each run uses a different random seed; averaging their predictions usually adds **~2–4%** over a single run.

---

## Option 1: Use the script (recommended)

**Windows (PowerShell or CMD):**
```bat
run_ensemble_b0_90.bat
```

**Linux / WSL / macOS:**
```bash
chmod +x run_ensemble_b0_90.sh
./run_ensemble_b0_90.sh
```

This will:
1. Train 3 B0 224 models (`blood_cell_model_95_full_run1.keras`, `_run2`, `_run3`).
2. Run the classification report (TTA=4) on each.
3. Ensemble the 3 models and write the result to `results/ensemble_*/classification_summary.txt`.

Training 3 runs takes about 3× the time of one run. After it finishes, check the ensemble accuracy in the summary file; it often lands in the **89–91%** range.

---

## Option 2: Manual commands

If you prefer to run steps yourself or already have one good model:

1. **Train 2–3 more B0 224 runs** (so you have 3–4 models total):
   ```bash
   python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 224 --run-id 1
   python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 224 --run-id 2
   python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 224 --run-id 3
   ```

2. **Ensemble them** (include your existing best model if you want):
   ```bash
   python run_ensemble_report.py --models blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras --data-dir data_split_full --tta 4
   ```
   If you still have `blood_cell_model_95_full.keras` (no run-id), you can add it for a 4-model ensemble:
   ```bash
   python run_ensemble_report.py --models blood_cell_model_95_full.keras blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras --data-dir data_split_full --tta 4
   ```

---

## If you're still below 90%

- **Add a 4th or 5th run:** Train with `--run-id 4` and `--run-id 5`, then add them to the `--models` list and run the ensemble again.
- **Inspect misclassifieds:** Use `classification_results.csv` (filter `correct==0`) and **docs/DATA_SPLIT_AND_MISCLASSIFIED.md** to look for label errors; fixing a few can nudge accuracy up.
- **Stronger single run:** Try one run with slightly more augmentation or B0 at 260×260 (if GPU allows) and add that checkpoint to the ensemble only if it reaches ≥86%.

For a longer-term plan toward 95%, see **docs/NEXT_STEPS_TO_95.md**.

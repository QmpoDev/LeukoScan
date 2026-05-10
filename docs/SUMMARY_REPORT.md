# Blood Cell Classification — Summary Report

A single reference for the current project state, results, and next steps. Use this to research further before running the ensemble pipeline.

---

## 1. Project overview

| Item | Description |
|------|-------------|
| **Task** | Image classification: 4 blood cell types — **Eosinophil**, **Lymphocyte**, **Monocyte**, **Neutrophil**. |
| **Dataset** | [BCCD / Blood Cell Images](https://github.com/Shenggan/BCCD_Dataset) (dataset2-master). Images in `data_raw/dataset2-master/dataset2-master/images/` with TRAIN/TEST and one folder per class. Labels = folder name (no separate CSV for this split). |
| **Splits** | `prepare_data.py` builds **data_split_4000** (4k subset) or **data_split_full** (~12.4k). **TRAIN** = original TRAIN only; **VAL** + **TEST** = 50/50 split of original TEST per class. Seed 42. |
| **Test set size** | After the current `prepare_data.py --full` split: **~half of original TEST** (~1.2k images total, counts per class vary). Older docs used 2,487 (100% of TEST as test). |
| **Stack** | TensorFlow/Keras; transfer learning with EfficientNetB0/B1 (ImageNet), 224×224 or 260×260, two-phase fine-tuning. |

---

## 2. Current results (full test set)

### Best model

- **Model:** `blood_cell_model_95_full.keras` — EfficientNetB0, 224×224, two-phase fine-tuning.
- **Test accuracy:** **87.13%** (with TTA=4).
- **Evaluation:** `run_classification_report.py --model blood_cell_model_95_full.keras --data-dir data_split_full --tta 4`.

### Per-class accuracy (best model, TTA=4)

| Class       | Accuracy  | Notes |
|------------|-----------|--------|
| Eosinophil | 82.18%    | Hardest; often confused with Neutrophil. |
| Lymphocyte | **100%**  | No errors. |
| Monocyte   | 75.00%    | Hard; often confused with Neutrophil. |
| Neutrophil | 91.35%    | Good; receives false positives from Eos/Mono. |

### Main confusions (best model)

- **Eosinophil → Neutrophil:** 111 errors.
- **Monocyte → Neutrophil:** 155 errors.
- **Neutrophil → Eosinophil:** 54 errors.
- **Lymphocyte:** 0 confusions.

So most errors are **Eosinophil vs Neutrophil** (both granulocytes) and **Monocyte vs Neutrophil**.

### Other models tried

- B0 “stronger” regularization: 85.85%.
- B1 224: 83.35%.
- B1 stronger + boost weak classes: 82.83%.
- **4-model ensemble (A+B+C+D):** 84.80% — worse than best single, because B1 models are weaker and dilute the average.

---

## 3. What is ensembling?

- **Idea:** Use **several trained models** (same architecture, different training runs/seeds). For each test image, **average their predicted class probabilities**, then take the class with the highest average (argmax).
- **Why it helps:** Different runs make different mistakes; averaging often reduces variance and can add **~2–4%** over a single model when all members are strong.
- **In this repo:** `run_ensemble_report.py` loads multiple `.keras` models, runs each on the test set (with optional TTA), averages probabilities, and writes accuracy + confusion matrix to `results/ensemble_*/`.

---

## 4. Planned run: reaching ~90% (before you run it)

### What the script does

**Scripts:** `run_ensemble_b0_90.bat` (Windows) or `run_ensemble_b0_90.sh` (Linux/WSL).

1. **Train 3 B0 224 models** (same config, different random seeds):  
   `blood_cell_model_95_full_run1.keras`, `_run2.keras`, `_run3.keras`.
2. **Run classification report (TTA=4)** for each run → `results/blood_cell_model_95_full_runN/`.
3. **Ensemble the 3 models** → average probabilities, report accuracy → `results/ensemble_*/classification_summary.txt`.

**Expected:** Ensemble accuracy often in **89–91%** range (vs 87% single). **Cost:** ~3× one full training run (time and compute).

### Prerequisites

- `data_split_full` already built: `python prepare_data.py --full`.
- Enough disk space for 3 extra models in `saved_model/`.
- Same environment as usual (TensorFlow, same Python).

### After the run

- **Ensemble accuracy:** `results/ensemble_blood_cell_model_95_full_run1_.../classification_summary.txt`.
- **Per-run accuracy:** `results/blood_cell_model_95_full_run1/`, `_run2`, `_run3` → each has `classification_summary.txt`.

---

## 5. Key files and scripts

| File / folder | Purpose |
|---------------|---------|
| `prepare_data.py` | Build data_split_4000 or data_split_full from data_raw. |
| `verify_data_split.py` | Check that the split did not put any image in the wrong class. |
| `training_transfer_95.py` | Train EfficientNet B0/B1; options: `--backbone`, `--size`, `--run-id`, `--boost-weak`, `--focal`. |
| `run_classification_report.py` | Single-model evaluation on TEST; writes results/<model_stem>/. |
| `run_ensemble_report.py` | Ensemble several models; writes results/ensemble_*/. |
| `run_ensemble_b0_90.bat` / `.sh` | Full pipeline: 3 B0 runs + reports + ensemble (aim ~90%). |
| `results/<model_stem>/` | Per-model: classification_summary.txt, classification_results.csv, confusion_matrix.csv. |
| `docs/` | All written docs (comparison, next steps, data labels, etc.). |

---

## 6. Docs in this repo (for further research)

| Doc | Use it to |
|-----|------------|
| **RESULTS_MODEL_COMPARISON.md** | See all model accuracies, per-class table, where results live. |
| **CONCLUSION_AND_IMPROVEMENTS.md** | Understand why B0 wins, why the 4-model ensemble failed, how to improve. |
| **NEXT_STEPS_TO_95.md** | Prioritized plan toward 95% (data/labels, B0-only ensemble, training tweaks). |
| **REACH_90.md** | Quick path to ~90%: script usage and manual ensemble commands. |
| **TARGET_95_ACCURACY.md** | Why 95%, what levers exist (transfer, two-phase, regularization, ensemble). |
| **PATH_TO_95.md** | Commands and pipeline (training, report, ensemble). |
| **DATA_RAW_AND_LABELS.md** | data_raw structure; confirm no mislabeling from the split script. |
| **DATA_SPLIT_AND_MISCLASSIFIED.md** | How train/val/test are built; how to inspect misclassified images. |
| **GPU_SETUP.md** | GPU options if you need faster training. |

---

## 7. Research topics (concepts to look up)

- **Transfer learning / fine-tuning:** Pretrained ImageNet backbone (EfficientNet), then train head and optionally unfreeze backbone with low learning rate.
- **Two-phase fine-tuning:** Phase 1 = freeze backbone, train head; Phase 2 = unfreeze, low LR. Reduces catastrophic forgetting.
- **Test-time augmentation (TTA):** Predict on original + flipped/rotated copies, average probabilities. We use TTA=4 (hflip + vflip combinations).
- **Ensemble methods:** Soft voting (average probabilities) vs hard voting (majority class). We use soft voting.
- **Class imbalance:** Class weights, focal loss, oversampling — we use class weights; focal/boost-weak were tried with mixed results.
- **EfficientNet:** Scalable CNN (B0, B1, …); good accuracy/speed trade-off; expects 224×224 or similar.
- **Confusion matrix:** Rows = true class, columns = predicted; diagonals = correct.

---

## 8. One-paragraph summary

This project classifies blood cell images (Eosinophil, Lymphocyte, Monocyte, Neutrophil) using BCCD data. The best single model is EfficientNetB0 224×224 at **87.13%** test accuracy; Eosinophil and Monocyte are the hardest classes and are often confused with Neutrophil. Ensembling means averaging predictions from multiple models (e.g. 3 B0 runs) to aim for ~90%. The script `run_ensemble_b0_90.bat` (or `.sh`) trains 3 such runs and ensembles them; results go to `results/ensemble_*/classification_summary.txt`. For deeper work, use the docs above and the concepts in section 7.

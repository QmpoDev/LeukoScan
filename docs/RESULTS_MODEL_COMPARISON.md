# Model Comparison and Results (Full Dataset, Test Set)

Comparison of all trained models on **data_split_full** (test set: 2,487 images). All transfer-learning models use **TTA=4** unless noted. Evaluation: `run_classification_report.py` or `run_ensemble_report.py` with `--data-dir data_split_full`.

---

## 1. Overview

| Model | Type | Test accuracy | Notes |
|-------|------|---------------|--------|
| **blood_cell_model_95_full** | EfficientNetB0, 224×224 | **87.13%** | Best single model. Baseline transfer. |
| blood_cell_model_95_stronger_full | EfficientNetB0, 224×224, stronger reg. | 85.85% | More dropout, label smoothing, augmentation. |
| blood_cell_model_95_B1_224_full | EfficientNetB1, 224×224 | 83.35% | Larger backbone; early stopped at epoch 24. |
| blood_cell_model_95_stronger_boostweak_B1_224_full | EfficientNetB1, 224×224, stronger + boost weak | 82.83% | B1 + stronger + Eosinophil/Monocyte class weight boost. |
| **4-model ensemble** (A+B+C+D) | Average probs, then argmax, TTA=4 | **84.80%** | Lower than best single (B1 models dilute). |
| blood_cell_model_full (custom CNN) | Custom CNN, 150×150 | ~80.86% | Previous best before transfer learning. |
| blood_cell_model_4000 (custom CNN) | Custom CNN, 4000 subset | ~62.67% | 600 test images; subset only. |

**Best overall:** **Model A (blood_cell_model_95_full)** at **87.13%** with TTA=4.

---

## 2. Per-class accuracy (transfer-learning models, TTA=4)

Test set: 2,487 images (Eosinophil 623, Lymphocyte 620, Monocyte 620, Neutrophil 624).

| Class | Model A (B0) | Model B (B0 strong) | Model C (B1) | Model D (B1 strong+boost) | 4-model ensemble |
|-------|--------------|----------------------|--------------|----------------------------|------------------|
| **Eosinophil** | **82.18%** | 75.92% | 68.54% | 67.90% | 71.75% |
| **Lymphocyte** | **100%** | **100%** | **100%** | **100%** | **100%** |
| **Monocyte** | **75.00%** | **75.00%** | 72.74% | 69.03% | **75.00%** |
| **Neutrophil** | 91.35% | 92.47% | 92.15% | **94.39%** | 92.47% |
| **Overall** | **87.13%** | 85.85% | 83.35% | 82.83% | 84.80% |

**Observations:**
- **Lymphocyte** is perfect across all models (easy class).
- **Eosinophil** and **Monocyte** are the hardest; most confusions are Eosinophil→Neutrophil and Monocyte→Neutrophil.
- B1 models (C, D) underperform B0 on this test set (likely more overfitting or different convergence).
- Ensemble is pulled down by weaker B1 models; best single model (A) is preferred for deployment.

---

## 3. Confusion patterns (best model: A)

From `results/blood_cell_model_95_full/classification_summary.txt`:

- **Eosinophil:** 111 predicted as Neutrophil (main error).
- **Monocyte:** 155 predicted as Neutrophil (main error).
- **Neutrophil:** 54 predicted as Eosinophil.
- No Lymphocyte confusions.

So the main confusion is **granulocytes (Eosinophil vs Neutrophil)** and **Monocyte vs Neutrophil**. See `docs/DATA_SPLIT_AND_MISCLASSIFIED.md` for how to inspect misclassified images for label noise.

---

## 4. Where results live

| Output | Path |
|--------|------|
| Per-model reports | `results/<model_stem>/classification_summary.txt`, `classification_results.csv`, `confusion_matrix.csv` |
| 4-model ensemble | `results/ensemble_blood_cell_model_95_full_blood_cell_model_95_stronger_full_b/` |
| Comparison (this doc) | `docs/RESULTS_MODEL_COMPARISON.md` |
| Conclusions and how to improve | `docs/CONCLUSION_AND_IMPROVEMENTS.md` |

---

## 5. How to reproduce

1. **Data:** `python prepare_data.py --full`
2. **Train one model (e.g. best):**  
   `python training_transfer_95.py --data-dir data_split_full --backbone B0 --size 224`
3. **Report (TTA=4):**  
   `python run_classification_report.py --model blood_cell_model_95_full.keras --data-dir data_split_full --tta 4`
4. **Full pipeline (4 models + ensemble):**  
   `bash run_all_95.sh` (after `sed -i 's/\r$//' run_all_95.sh` on WSL if needed).

See **README.md** and **docs/PATH_TO_95.md** for full commands and options.

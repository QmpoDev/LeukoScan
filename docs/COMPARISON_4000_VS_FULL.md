# Breakdown & Comparison: 4000-Subset vs Full Dataset

Same model and pipeline (CNN with BatchNorm, L2, augmentation, class weights, ReduceLROnPlateau, label smoothing); only dataset size and **test set** change. Each model is evaluated on **its own** test set (4k → 600 images, full → 2,487 images). This run was done in WSL2 with GPU (GTX 1660 SUPER).

---

## 1. Dataset breakdown

| Split   | data_split_4000 | data_split_full |
|--------|------------------|-----------------|
| **Train** | 2,800        | 6,968           |
| **Val**   | 600          | 2,989           |
| **Test**  | 600          | 2,487           |
| **Total** | 4,000        | 12,444          |

Full dataset has **~2.5×** training images and **~4×** test images.

---

## 2. Training summary

| Metric                        | 4000 subset              | Full dataset               |
|-------------------------------|--------------------------|----------------------------|
| Data dir                      | data_split_4000           | data_split_full            |
| Steps per epoch               | 87                        | 217                        |
| Best epoch (restored)         | 23                        | 43                         |
| Val accuracy (best epoch)     | 82.47%                    | 99.83%                     |
| Test accuracy (from training.py) | 65.33%                | 82.27%                     |

Full-dataset run used further dialed-down enhancements (label smoothing 0.01, L2 3e-5, rotation 0.08, dropout 0.35); restored best at epoch 43. **Report test accuracy 80.86%** (above 80% target).

---

## 3. Classification report (each model on its own test set)

From `python run_classification_report.py --model blood_cell_model_4000.keras` (uses `data_split_4000/TEST`) and `--model blood_cell_model_full.keras` (uses `data_split_full/TEST`):

| Metric          | 4000 subset (600 test) | Full dataset (2,487 test) |
|-----------------|-------------------------|----------------------------|
| Test images     | 600                      | 2,487                      |
| Correct         | 376                      | 2,011                      |
| **Test accuracy** | **62.67%**             | **80.86%**                 |

Latest run: full-dataset model **80.86%** (further dialed-down: label smoothing 0.01, L2 3e-5, rotation 0.08, dropout 0.35; best epoch 43). Full model is the preferred checkpoint for deployment.

---

## 4. Per-class accuracy (from classification report)

### 4000 subset (600 test images)

| Class      | Accuracy | Correct / Total |
|------------|----------|-----------------|
| Eosinophil | 58.00%   | 87 / 150        |
| Lymphocyte | 63.33%   | 95 / 150        |
| Monocyte   | 58.00%   | 87 / 150        |
| Neutrophil | 71.33%   | 107 / 150       |

### Full dataset (2,487 test images)

| Class      | Accuracy | Correct / Total |
|------------|----------|-----------------|
| Eosinophil | 75.44%   | 470 / 623       |
| Lymphocyte | 84.03%   | 521 / 620       |
| Monocyte   | 73.06%   | 453 / 620       |
| Neutrophil | 90.87%   | 567 / 624       |

- **Neutrophil** 90.87%, **Lymphocyte** 84.03%, **Eosinophil** 75.44%, **Monocyte** 73.06%. All classes above 73%.
- Main confusions: 4k spreads errors across classes; full model’s main errors are Eosinophil→Neutrophil (117), Monocyte→Neutrophil (235).

---

## 5. Confusion (where the model goes wrong)

### 4000 subset (600 test)

- **Eosinophil:** 87 correct, 31 as Lymphocyte, 32 as Neutrophil.
- **Lymphocyte:** 95 correct, 25 as Eosinophil, 26 as Neutrophil.
- **Monocyte:** 87 correct, 12 as Eosinophil, **51 as Neutrophil** (main error).
- **Neutrophil:** 107 correct, 26 as Eosinophil, 15 as Lymphocyte.

### Full dataset (2,487 test) — further dialed-down (80.86% run)

- **Eosinophil:** 470 correct, 2 as Lymphocyte, **151 as Neutrophil** (main error).
- **Lymphocyte:** 521 correct, 37 as Eosinophil, 30 as Monocyte, 32 as Neutrophil.
- **Monocyte:** 453 correct, 31 as Eosinophil, **136 as Neutrophil** (main error).
- **Neutrophil:** 567 correct, 46 as Eosinophil, 6 as Lymphocyte, 5 as Monocyte.

**Pattern:** Eosinophil ↔ Neutrophil and Monocyte → Neutrophil remain the main confusions for both models; the full model has stronger per-class accuracy overall.

---

## 6. Takeaway

| Question | Answer |
|----------|--------|
| **This run** | 4k: **62.67%** (600 test). Full: **80.86%** (2,487 test). Further dialed-down: label smoothing 0.01, L2 3e-5, rotation 0.08, dropout 0.35; best epoch 43. |
| **Best class (4k)** | Neutrophil 71.33%, Lymphocyte 63.33%, Eosinophil and Monocyte 58%. |
| **Best class (full)** | Neutrophil 90.87%, Lymphocyte 84.03%, Eosinophil 75.44%, Monocyte 73.06%. |
| **Hardest class** | Eosinophil and Monocyte for 4k (58%); Monocyte for full (73.06%). Main confusions: Eosinophil→Neutrophil (151), Monocyte→Neutrophil (136). |
| **Practical choice** | Use the **full-dataset model** for deployment (**80.86%** test accuracy, above 80% target). |

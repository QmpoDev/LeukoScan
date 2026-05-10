# Results: Blood Cell Classification (Full Dataset)

This document records the **results** for the model trained on the **full dataset** (~12.5k images). Compare with [RESULTS_4000_SUBSET.md](RESULTS_4000_SUBSET.md).

---

## 1. Process Used

1. **Data preparation:** `python prepare_data.py --full` → writes to **`data_split_full/`**
   - **Current script:** all original TRAIN → train; original TEST split 50/50 → val and test (per class, seed 42).
   - **Older runs** (before that change): 6,968 train, 2,989 val, 2,487 test (12,444 total). Re-run `prepare_data.py --full` and `check_data_split.py --data-dir data_split_full --full` for exact counts.

2. **Verification (optional):** `python check_data_split.py --data-dir data_split_full --full`

3. **Training:** `python training.py --data-dir data_split_full` (or `python training.py`; default is data_split_full). Saves `saved_model/blood_cell_model_full.keras`.

4. **Classification report:** `python run_classification_report.py --model blood_cell_model_full.keras` → uses `data_split_full/TEST` (about half of original TEST after the split change), writes to `results/blood_cell_model_full/`.

---

## 2. Training Setup

Same as 4000 subset: see [RESULTS_4000_SUBSET.md](RESULTS_4000_SUBSET.md) §2 and §3. Only the dataset size and thus `steps_per_epoch` / `validation_steps` change.

---

## 3. Training Run

Full dataset: 6,968 train, 2,989 val, 2,487 test. 217 steps/epoch, 50 epochs. **Dialed-down enhanced** (further): LR 1e-4, label smoothing **0.01**, L2 **3e-5**, rotation **0.08**, zoom 0.05, noise 0.01, Dense dropout **0.35**, patience 32, ReduceLROnPlateau 10. WSL2 GPU run; restored best at epoch 43.

```
Epoch 43/50  (best val_loss)
217/217 - 26s 119ms/step - accuracy: 0.9960 - loss: 0.1094 - val_accuracy: 0.9983 - val_loss: 0.0971
...
Restoring model weights from the end of the best epoch: 43.
78/78 - 3s - 36ms/step - accuracy: 0.8227 - loss: 0.6298

Test accuracy: 0.8226779103279114
Model saved to saved_model/blood_cell_model_full.keras.
```

**Best epoch (restored):** 43  
**Validation accuracy at best epoch:** 0.9983 (99.83%)  
**Test accuracy (from training script):** 0.8227 (82.27%)

---

## 4. Classification Report (test set)

From `python run_classification_report.py --model blood_cell_model_full.keras` (2,487 test images). Summary from `results/blood_cell_model_full/classification_summary.txt`:

**Test accuracy (from report):** 0.8086 (**80.86%**)  
**Correct:** 2,011 / 2,487

| Class      | Accuracy | Correct / Total |
|------------|----------|-----------------|
| Eosinophil | 75.44%   | 470 / 623       |
| Lymphocyte | 84.03%   | 521 / 620       |
| Monocyte   | 73.06%   | 453 / 620       |
| Neutrophil | 90.87%   | 567 / 624       |

**Confusion matrix (rows=true, cols=predicted):**

|              | Eosinophil | Lymphocyte | Monocyte | Neutrophil |
|--------------|------------|------------|----------|------------|
| Eosinophil   | 470        | 2          | 0        | 151        |
| Lymphocyte   | 37         | 521        | 30       | 32         |
| Monocyte     | 31         | 0          | 453      | 136        |
| Neutrophil   | 46         | 6          | 5        | 567        |

---

## 5. Comparison with 4000-Subset Baseline

Each model is evaluated on **its own** test set (4k → 600 images, full → 2,487 images). This run used the enhanced pipeline (GPU, class weights, augmentation, ReduceLROnPlateau, etc.):

| Metric                  | 4000 subset (600 test) | Full dataset (2,487 test) |
|-------------------------|------------------------|---------------------------|
| Test accuracy (report)  | 62.67%                 | **80.86%**                |
| Best epoch              | 23                     | 43                        |
| Train size              | 2,800                  | 6,968                     |

**Notes:** Latest full-dataset run used **further dialed-down** enhancements (label smoothing 0.01, L2 3e-5, rotation 0.08, dropout 0.35); report accuracy **80.86%** — above 80% target and in range of original un-enhanced (~84–86%). See [COMPARISON_4000_VS_FULL.md](COMPARISON_4000_VS_FULL.md) for full breakdown.

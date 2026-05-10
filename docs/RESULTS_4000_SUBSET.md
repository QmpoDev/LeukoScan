# Results: Blood Cell Classification (4000-Image Subset)

This document records the **process**, **training setup**, and **results** for the model trained on the 4000-image subset. Use it as a baseline to compare with the full-dataset run later.

---

## 1. Process Used

1. **Data preparation**
   - Source: `data_raw/dataset2-master/dataset2-master/images/` (BCCD dataset).
   - Script: `python prepare_data.py` (default 4000 subset) → writes to **`data_split_4000/`**.
   - Split: **700/class from TRAIN**; **150 val + 150 test/class from TEST** → **2800 train, 600 val, 600 test** (same totals; val/test no longer taken from TRAIN).

2. **Verification**
   - `python check_data_split.py --data-dir data_split_4000` to confirm 2800/600/600.

3. **Training**
   - `python training.py --data-dir data_split_4000` → reads `data_split_4000/TRAIN` and `data_split_4000/VAL`, saves `saved_model/blood_cell_model_4000.keras`, reports test accuracy at the end.

4. **Classification and report**
   - Single image: `python classify.py path/to/image.jpg [saved_model/blood_cell_model_4000.keras]`
   - Full test set: `python run_classification_report.py --model blood_cell_model_4000.keras` → uses `data_split_4000/TEST` (600 images), writes to `results/blood_cell_model_4000/`.

---

## 2. Training Code Summary (`training.py`)

- **Data:** `image_dataset_from_directory` for TRAIN, VAL, TEST. Train uses augmentation (flip, rotation, zoom, noise) and `.repeat()`. Validation and test are normalized only.
- **Input size:** 150×150 RGB.
- **Model:** Sequential CNN with BatchNorm after each Conv2D, L2 regularization, Dense(256): 4× (Conv2D → BatchNorm → MaxPooling2D), Flatten → Dropout(0.25) → Dense(256) → Dropout(0.5) → Dense(4, softmax).
- **Optimizer:** Adam, learning rate 7e-5. Loss: CategoricalCrossentropy with label_smoothing=0.1.
- **Callbacks:** EarlyStopping (val_loss, patience 32) and ReduceLROnPlateau (factor 0.5, patience 10). Class weights used for imbalance.
- **Training:** Up to 50 epochs (87 train steps, 19 val steps for 4000 subset). Run on WSL2 with GPU (e.g. GTX 1660 SUPER).

---

## 3. How It Was Trained

| Setting            | Value |
|--------------------|--------|
| Dataset            | 4000-image subset (2800 train / 600 val / 600 test) |
| Batch size         | 32 |
| Image size         | 150×150 |
| Max epochs         | 50 |
| Early stopping     | val_loss, patience 32; ReduceLROnPlateau factor 0.5, patience 10 |
| Regularization     | L2 on conv layers, Dropout 0.25 / 0.5, label smoothing 0.1, class weights |


---

## 4. Training Run

From `python training.py --data-dir data_split_4000` in WSL2 (GPU). Enhanced setup: class weights, BatchNorm, L2, augmentation, ReduceLROnPlateau (patience 10), label smoothing, LR 7e-5, early-stopping patience 32.

```
Epoch 23/50  (best val_loss)
87/87 - 10s 110ms/step - accuracy: 0.8291 - loss: 0.7809 - val_accuracy: 0.8247 - val_loss: 0.7859
...
Epoch 50/50
Restoring model weights from the end of the best epoch: 23.
19/19 - 2s - 91ms/step - accuracy: 0.6533 - loss: 1.0843

Test accuracy: 0.653333306312561
Model saved to saved_model/blood_cell_model_4000.keras.
```

**Best epoch (restored):** 23  
**Validation accuracy at best epoch:** 0.8247 (82.47%)  
**Test accuracy (from training script):** 0.6533 (65.33%)

---

## 5. Classification Report (test set)

From `python run_classification_report.py --model blood_cell_model_4000.keras` on **data_split_4000/TEST** (600 images). Summary from `results/blood_cell_model_4000/classification_summary.txt`:

**Test accuracy (from report):** 0.6267 (**62.67%**)  
**Correct:** 376 / 600

**Per-class accuracy:**

| Class      | Accuracy | Correct / Total |
|------------|----------|-----------------|
| Eosinophil | 58.00%   | 87 / 150        |
| Lymphocyte | 63.33%   | 95 / 150        |
| Monocyte   | 58.00%   | 87 / 150        |
| Neutrophil | 71.33%   | 107 / 150       |

**Confusion matrix (rows=true, cols=predicted):**

|              | Eosinophil | Lymphocyte | Monocyte | Neutrophil |
|--------------|------------|------------|----------|------------|
| Eosinophil   | 87         | 31         | 0        | 32         |
| Lymphocyte   | 25         | 95         | 4        | 26         |
| Monocyte     | 12         | 0          | 87       | 51         |
| Neutrophil   | 26         | 15         | 2        | 107        |

---

## 6. Notes

- This run is the **4000-subset baseline**, evaluated on its **own** 600-image test set (`data_split_4000/TEST`). The full-dataset model is evaluated on `data_split_full/TEST` (2,487 images); see [RESULTS_FULL_DATASET.md](RESULTS_FULL_DATASET.md) and [COMPARISON_4000_VS_FULL.md](COMPARISON_4000_VS_FULL.md).
- Classification outputs for the 4000 model are in `results/blood_cell_model_4000/`.

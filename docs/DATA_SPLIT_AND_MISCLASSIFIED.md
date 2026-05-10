# Data Split and Inspecting Misclassifications

## How the split is done (`prepare_data.py`)

- **Source:** `data_raw/dataset2-master/dataset2-master/images/` with folders `TRAIN` and `TEST` (class subfolders: EOSINOPHIL, LYMPHOCYTE, MONOCYTE, NEUTROPHIL).
- **Same staining/scanner:** All images come from the same dataset; there is no explicit stratification by staining or scanner. **Train** uses only the original **TRAIN** folder; **val** and **test** use only the original **TEST** folder (disjoint 50/50 split per class), so no file from the training source pool appears in validation.
- **Full dataset** (`python prepare_data.py --full` → `data_split_full`):
  - **Train:** **All** images in each class from **TRAIN** (seed 42 shuffle before copy; every file is used).
  - **Val:** First half of images in each class from **TEST** (after shuffle, seed 42).
  - **Test:** Second half of images in each class from **TEST**.
- **Subset** (`python prepare_data.py` → `data_split_4000`):
  - **Train:** 700 images per class from **TRAIN** only.
  - **Val / test:** 150 + 150 per class from **TEST** only (shuffle then first 150 → val, next 150 → test).
- **Comparability:** **Val** and **test** are two halves of the same **TEST** source (same distribution). **Train** may differ from them if the dataset authors separated **TRAIN** vs **TEST** by acquisition or batch (common in benchmarks).

## Checking for label noise or ambiguity

Classes that often lag or confuse with others: **Eosinophil** and **Monocyte** (e.g. confused with Neutrophil or each other). To check for label noise or ambiguous cases:

1. **Run a classification report** so you have per-image predictions:
   ```bash
   python run_classification_report.py --model blood_cell_model_95_stronger_full.keras --data-dir data_split_full
   ```
   This writes `results/<model_stem>/classification_results.csv` with columns: `image`, `true_class`, `predicted_class`, `confidence`, `correct`.

2. **List misclassified images** (e.g. in Python or Excel):
   - Open `classification_results.csv` and filter to `correct == 0`.
   - Optionally filter by `true_class` (e.g. Eosinophil or Monocyte) and `predicted_class` to see confusions like Eosinophil→Neutrophil or Monocyte→Lymphocyte.

3. **Inspect visually:** For a given (true_class, predicted_class) pair, open the listed image paths (under `data_split_full/TEST/<true_class>/<image>`) and check:
   - **Label errors:** Image actually looks like the predicted class → consider relabeling or excluding from training.
   - **Ambiguity:** Image is borderline between two classes → may be acceptable to keep; focal loss or higher class weight for that class can help the model focus on these.

4. **Quick script idea** (optional): A small script could read `classification_results.csv`, filter `correct == 0`, and group by `(true_class, predicted_class)` to print counts and optionally copy misclassified files to a folder for review.

## Summary

- Train is from original TRAIN only; val and test are disjoint halves of original TEST (full or 300-image draw per class in the 4k subset).
- To check misclassified Eosinophil/Monocyte: use `classification_results.csv` (correct=0), filter by true/predicted class, then visually inspect those images for label noise or ambiguity.

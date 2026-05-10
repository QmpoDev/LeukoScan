# data_raw Structure and Labeling

This doc explains how **data_raw** is organized, how **prepare_data.py** uses it, and why the split script **does not introduce mislabeling**. It also clarifies how you can verify that training uses the same labels as the original dataset.

---

## 1. What is in data_raw?

The repo has two dataset layouts under `data_raw/`:

| Path | Structure | Use in this project |
|------|-----------|----------------------|
| **dataset2-master/dataset2-master/images/** | `TRAIN/` and `TEST/`; under each: `EOSINOPHIL/`, `LYMPHOCYTE/`, `MONOCYTE/`, `NEUTROPHIL/` (one image per file). | **Yes.** This is the source for `prepare_data.py`. Labels are **folder-based**: the class of an image is the folder it sits in. |
| **dataset-master/dataset-master/** | `JPEGImages/` (full slides, e.g. BloodImage_00000.jpg), `Annotations/*.xml` (object boxes), `labels.csv` (Image index → Category per full image). | **No.** Different format (full images + CSV labels). Used for other BCCD tasks (e.g. detection). |

So for our classification pipeline, the **original labels** are the folder names in **dataset2-master/.../images**:  
`TRAIN/EOSINOPHIL/`, `TRAIN/LYMPHOCYTE/`, etc. There is no separate label file for dataset2-master; the folder *is* the label.

---

## 2. What prepare_data.py does (no relabeling)

- **Source:** `data_raw/dataset2-master/dataset2-master/images/` (TRAIN + TEST, each with 4 class folders).
- **Destination:** `data_split_4000/` or `data_split_full/` with `TRAIN/`, `VAL/`, `TEST/` and class subfolders (Title Case: Eosinophil, Lymphocyte, Monocyte, Neutrophil).

**Copy logic (no cross-class mixing):**

1. For each **source class** (e.g. `EOSINOPHIL`), it only reads from that class folder: `TRAIN_SRC / "EOSINOPHIL"`, `TEST_SRC / "EOSINOPHIL"`.
2. It copies files **only** into the **matching** destination class folder: `dest / "TRAIN" / "Eosinophil"` (same class, different casing).
3. The mapping is fixed: `EOSINOPHIL` → `Eosinophil`, `LYMPHOCYTE` → `Lymphocyte`, `MONOCYTE` → `Monocyte`, `NEUTROPHIL` → `Neutrophil`. A file from `TRAIN/EOSINOPHIL/` is never written to `TRAIN/Lymphocyte/` or any other class.

So **prepare_data.py does not relabel and does not put an image in the wrong class**. It only:

- Copies files from the original class folder to the same class in the split (with consistent naming).
- Builds **VAL** and **TEST** from the original **TEST** folder only (50/50 per class for full; 150+150 per class from TEST for the 4k subset). **TRAIN** uses only the original **TRAIN** folder, so training and validation images never share the same source pool.

If there is mislabeling, it would already exist in **data_raw** (wrong file in the wrong class folder), not introduced by the script.

---

## 3. Can we train directly from data_raw?

- **Current setup:** Training scripts expect a directory with **TRAIN**, **VAL**, and **TEST** (each with class subfolders). The original `data_raw/.../images` has only **TRAIN** and **TEST** (no VAL). So we use `prepare_data.py` to build a copy that includes VAL.
- **Training from data_raw without copying:** You could point training at `data_raw` and build **VAL/TEST** from original **TEST** with the same 50/50 rule (fixed seed) instead of using `prepare_data.py` copies.
- **Conclusion:** Training is already **based on the same labeling as the original dataset** (folder = class). The split script only copies and assigns train/val/test; it does not change which class an image belongs to.

---

## 4. How to verify the split did not introduce wrong-class copies

Run the verification script (see below) so that for every image in `data_split_4000` or `data_split_full`:

- Each file in `data_split_*/TRAIN/<Class>/` is found in `data_raw/.../images/TRAIN/<SameClass>/` (same filename).
- Each file in `data_split_*/VAL/<Class>/` and `data_split_*/TEST/<Class>/` is found in `data_raw/.../images/TEST/<SameClass>/` (same filename).

If this passes, no image was copied into a different class by the script.

---

## 5. About labels.csv in data_raw

- **dataset2-master** and **dataset-master** each have a **labels.csv** (Image index → Category). Those CSVs refer to the **dataset-master** style (full images like BloodImage_00000.jpg). They include categories like BASOPHIL, multi-label cells, and empty entries.
- **dataset2-master/images** is a different, pre-built layout: cropped/augmented images already placed in class folders (EOSINOPHIL, etc.). Our pipeline uses **only** that folder structure; we do not read labels.csv for dataset2-master when preparing or training. So training is “from the original dataset” in the sense that we use the **folder-based labels** of dataset2-master, not the CSV.

---

## 6. Quick reference

| Question | Answer |
|----------|--------|
| Where do “original” labels come from? | Folder names in `data_raw/dataset2-master/dataset2-master/images/` (TRAIN/ and TEST/ with 4 class subfolders). |
| Does prepare_data.py change labels or put an image in the wrong class? | No. It only copies; each file stays in the same class (with fixed EOSINOPHIL→Eosinophil etc.). |
| How can I be sure? | Run `python verify_data_split.py --data-dir data_split_full` (or data_split_4000). It checks every copied file exists in data_raw under the same class. |
| Can we train from data_raw directly? | Labels would be the same (folder = class). Today we use a copied split with TRAIN/VAL/TEST; you could mirror the same rules (TRAIN only → train; TEST split → val/test) without copying. |

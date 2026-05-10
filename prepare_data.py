"""
Laboratory 2 - Data Preparation

Avoids train/val leakage from the same source folder (e.g. pre-augmented duplicates in TRAIN):

- TRAIN: 100% of images from the original TRAIN source (no images from TRAIN go to VAL).
- VAL + TEST: 50/50 split of images from the original TEST source (per class, seed 42).

Subset (default): 4000 images — 700 train per class from TRAIN; 150 val + 150 test per class from TEST.
Full (--full): all TRAIN → TRAIN; half of each class's TEST → VAL, half → TEST.
"""

import argparse
import shutil
import random
from pathlib import Path

# Reproducible splits
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Paths (project root = folder containing this script)
PROJECT_ROOT = Path(__file__).resolve().parent
ORIGINAL = PROJECT_ROOT / "data_raw" / "dataset2-master" / "dataset2-master" / "images"
# DEST set in main: data_split_4000 (subset) or data_split_full (full dataset)
DEST = PROJECT_ROOT / "data_split_4000"

# Class names: source folders are UPPERCASE, destination use Title Case
CLASS_MAP = {
    "EOSINOPHIL": "Eosinophil",
    "LYMPHOCYTE": "Lymphocyte",
    "MONOCYTE": "Monocyte",
    "NEUTROPHIL": "Neutrophil",
}

# Subset (4000 images): 700/class from TRAIN; 150 val + 150 test/class from TEST (50/50 of 300 drawn from TEST)
SPLIT_PER_CLASS_SUBSET = {
    "EOSINOPHIL": (700, 150, 150),
    "LYMPHOCYTE": (700, 150, 150),
    "MONOCYTE": (700, 150, 150),
    "NEUTROPHIL": (700, 150, 150),
}

TRAIN_SRC = ORIGINAL / "TRAIN"
TEST_SRC = ORIGINAL / "TEST"


def list_images(folder: Path) -> list[Path]:
    """Return list of image files in folder (common extensions)."""
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    if not folder.exists():
        return []
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.upper() in {e.upper() for e in exts}]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def prepare_subset(dest: Path) -> None:
    """Prepare 4000-image subset: train from TRAIN only; val/test from TEST only (50/50 of TEST draw)."""
    if not TRAIN_SRC.exists():
        raise FileNotFoundError(f"TRAIN folder not found: {TRAIN_SRC}")
    if not TEST_SRC.exists():
        raise FileNotFoundError(f"TEST folder not found: {TEST_SRC}")

    for split in ("TRAIN", "VAL", "TEST"):
        for dest_class in CLASS_MAP.values():
            d = dest / split / dest_class
            if d.exists():
                for f in d.iterdir():
                    if f.is_file():
                        f.unlink()

    total_copied = 0
    for src_name, dest_name in CLASS_MAP.items():
        n_train, n_val, n_test = SPLIT_PER_CLASS_SUBSET[src_name]
        train_src_dir = TRAIN_SRC / src_name
        test_src_dir = TEST_SRC / src_name
        train_images = list_images(train_src_dir)
        test_images = list_images(test_src_dir)

        if len(train_images) < n_train:
            raise RuntimeError(f"Class {src_name}: TRAIN has {len(train_images)} images, need {n_train}")
        if len(test_images) < n_val + n_test:
            raise RuntimeError(
                f"Class {src_name}: TEST has {len(test_images)} images, need {n_val + n_test} for val+test"
            )

        random.shuffle(train_images)
        random.shuffle(test_images)
        train_selected = train_images[:n_train]
        val_selected = test_images[:n_val]
        test_selected = test_images[n_val : n_val + n_test]

        ensure_dir(dest / "TRAIN" / dest_name)
        ensure_dir(dest / "VAL" / dest_name)
        ensure_dir(dest / "TEST" / dest_name)
        for path in train_selected:
            shutil.copy2(path, dest / "TRAIN" / dest_name / path.name)
            total_copied += 1
        for path in val_selected:
            shutil.copy2(path, dest / "VAL" / dest_name / path.name)
            total_copied += 1
        for path in test_selected:
            shutil.copy2(path, dest / "TEST" / dest_name / path.name)
            total_copied += 1
        print(f"  {dest_name}: train={len(train_selected)}, val={len(val_selected)}, test={len(test_selected)}")

    print(f"\nDone. Total images copied: {total_copied} (expected 4000).")


def prepare_full(dest: Path) -> None:
    """Full dataset: all TRAIN → train; original TEST split 50/50 → val and test (per class)."""
    if not TRAIN_SRC.exists():
        raise FileNotFoundError(f"TRAIN folder not found: {TRAIN_SRC}")
    if not TEST_SRC.exists():
        raise FileNotFoundError(f"TEST folder not found: {TEST_SRC}")

    for split in ("TRAIN", "VAL", "TEST"):
        for dest_class in CLASS_MAP.values():
            d = dest / split / dest_class
            if d.exists():
                for f in d.iterdir():
                    if f.is_file():
                        f.unlink()

    total_copied = 0
    for src_name, dest_name in CLASS_MAP.items():
        train_src_dir = TRAIN_SRC / src_name
        test_src_dir = TEST_SRC / src_name
        train_images = list_images(train_src_dir)
        test_images = list_images(test_src_dir)

        random.shuffle(train_images)
        random.shuffle(test_images)
        train_selected = train_images
        mid = len(test_images) // 2
        val_selected = test_images[:mid]
        test_selected = test_images[mid:]

        ensure_dir(dest / "TRAIN" / dest_name)
        ensure_dir(dest / "VAL" / dest_name)
        ensure_dir(dest / "TEST" / dest_name)
        for path in train_selected:
            shutil.copy2(path, dest / "TRAIN" / dest_name / path.name)
            total_copied += 1
        for path in val_selected:
            shutil.copy2(path, dest / "VAL" / dest_name / path.name)
            total_copied += 1
        for path in test_selected:
            shutil.copy2(path, dest / "TEST" / dest_name / path.name)
            total_copied += 1
        print(f"  {dest_name}: train={len(train_selected)}, val={len(val_selected)}, test={len(test_selected)}")

    print(f"\nDone. Total images copied: {total_copied} (full dataset: all TRAIN + all TEST split 50/50 val/test).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare train/val/test: TRAIN from original TRAIN only; VAL+TEST from original TEST (50/50)."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full dataset → data_split_full; else 4000 subset → data_split_4000",
    )
    args = parser.parse_args()

    dest = PROJECT_ROOT / ("data_split_full" if args.full else "data_split_4000")

    print("Data preparation - Laboratory 2")
    print(f"Source: {ORIGINAL}")
    print(f"Destination: {dest}")
    print("Mode: FULL dataset" if args.full else "Mode: 4000 subset")
    print()
    if args.full:
        prepare_full(dest)
    else:
        prepare_subset(dest)

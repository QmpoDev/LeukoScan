"""
Validates a data split folder: structure and image counts.
Use --data-dir data_split_4000 or data_split_full (default: data_split_4000).
Use --full to only report counts (no expected-subset check; use for full-dataset).
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

CLASSES = ("Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil")
SPLITS = ("TRAIN", "VAL", "TEST")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

# Expected for 4000 subset
EXPECTED_SUBSET = {
    "Eosinophil": (700, 150, 150),
    "Lymphocyte": (700, 150, 150),
    "Monocyte": (700, 150, 150),
    "Neutrophil": (700, 150, 150),
}


def count_images(folder: Path) -> int:
    if not folder.exists():
        return -1
    return sum(
        1 for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )


def check_subset(data_split: Path) -> bool:
    all_ok = True
    split_totals = [0, 0, 0]
    if not data_split.exists():
        print(f"ERROR: folder not found: {data_split}")
        return False
    print(
        f"Checking {data_split.name} (expected: 4000 images; train from TRAIN only; val+test from TEST)\n"
    )
    print(f"{'Class':<12} {'TRAIN':>6} {'VAL':>6} {'TEST':>6}  {'Status':<8}")
    print("-" * 45)
    for class_name in CLASSES:
        exp = EXPECTED_SUBSET[class_name]
        row_ok = True
        counts = []
        for i, (split, exp_n) in enumerate(zip(SPLITS, exp)):
            n = count_images(data_split / split / class_name)
            if n < 0:
                n = 0
                row_ok = all_ok = False
            counts.append(n)
            split_totals[i] += n
            if n != exp_n:
                row_ok = all_ok = False
        print(f"{class_name:<12} {counts[0]:>6} {counts[1]:>6} {counts[2]:>6}  {'OK' if row_ok else 'MISMATCH':<8}")
    print("-" * 45)
    total_ok = sum(split_totals) == 4000 and split_totals == [2800, 600, 600]
    if not total_ok:
        all_ok = False
    print(f"{'TOTAL':<12} {split_totals[0]:>6} {split_totals[1]:>6} {split_totals[2]:>6}  {'OK' if total_ok else 'MISMATCH'}")
    return all_ok


def check_full(data_split: Path) -> bool:
    if not data_split.exists():
        print(f"ERROR: folder not found: {data_split}")
        return False
    print(f"{data_split.name} counts (full dataset)\n")
    print(f"{'Class':<12} {'TRAIN':>6} {'VAL':>6} {'TEST':>6}")
    print("-" * 40)
    split_totals = [0, 0, 0]
    for class_name in CLASSES:
        counts = []
        for i, split in enumerate(SPLITS):
            n = count_images(data_split / split / class_name)
            if n < 0:
                n = 0
            counts.append(n)
            split_totals[i] += n
        print(f"{class_name:<12} {counts[0]:>6} {counts[1]:>6} {counts[2]:>6}")
    print("-" * 40)
    print(f"{'TOTAL':<12} {split_totals[0]:>6} {split_totals[1]:>6} {split_totals[2]:>6}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data_split_4000", help="Data root to check (data_split_4000 or data_split_full)")
    parser.add_argument("--full", action="store_true", help="Report counts only, no expected-subset check (for full dataset)")
    args = parser.parse_args()
    data_split = PROJECT_ROOT / args.data_dir
    if args.full:
        check_full(data_split)
        print("\nDone.")
        exit(0)
    ok = check_subset(data_split)
    print("\n" + ("Data split is correct." if ok else "Data split has errors. Run prepare_data.py to fix."))
    exit(0 if ok else 1)

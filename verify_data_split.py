"""
Verify that data_split_4000 or data_split_full is a correct copy of data_raw:
every image in the split exists in the original dataset under the SAME class folder.
This confirms prepare_data.py did not put any image in the wrong class.

Usage:
  python verify_data_split.py --data-dir data_split_full
  python verify_data_split.py --data-dir data_split_4000
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ORIGINAL = PROJECT_ROOT / "data_raw" / "dataset2-master" / "dataset2-master" / "images"

# Destination uses Title Case; source uses UPPERCASE.
DEST_TO_SRC_CLASS = {
    "Eosinophil": "EOSINOPHIL",
    "Lymphocyte": "LYMPHOCYTE",
    "Monocyte": "MONOCYTE",
    "Neutrophil": "NEUTROPHIL",
}

# TRAIN in the split comes from original TRAIN only.
# VAL and TEST in the split both come from original TEST (50/50 per class).
ORIGINAL_SPLIT_FOR = {"TRAIN": "TRAIN", "VAL": "TEST", "TEST": "TEST"}


def list_images(folder: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    if not folder.exists():
        return []
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.upper() in {e.upper() for e in exts}]


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify data split: every file exists in data_raw under the same class.")
    parser.add_argument("--data-dir", type=str, required=True, help="data_split_full or data_split_4000")
    args = parser.parse_args()

    dest_root = Path(args.data_dir).resolve()
    if not dest_root.is_dir():
        raise FileNotFoundError(f"Not a directory: {dest_root}")

    if not ORIGINAL.exists():
        raise FileNotFoundError(f"Original dataset not found: {ORIGINAL}")

    errors = []
    checked = 0
    for split in ("TRAIN", "VAL", "TEST"):
        orig_split = ORIGINAL_SPLIT_FOR[split]
        for dest_class, src_class in DEST_TO_SRC_CLASS.items():
            dest_dir = dest_root / split / dest_class
            orig_dir = ORIGINAL / orig_split / src_class
            if not dest_dir.exists():
                continue
            for f in list_images(dest_dir):
                checked += 1
                orig_path = orig_dir / f.name
                if not orig_path.exists():
                    errors.append((f"Missing in original: {f.relative_to(dest_root)} (expected {orig_path})", None))
                elif orig_path.stat().st_size != f.stat().st_size:
                    errors.append((f"Size mismatch: {f.relative_to(dest_root)}", f"{f.stat().st_size} vs {orig_path.stat().st_size}"))

    if errors:
        print("Verification FAILED.")
        for msg, extra in errors[:50]:
            print(f"  {msg}" + (f" ({extra})" if extra else ""))
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more.")
        print(f"Total errors: {len(errors)}. Checked: {checked}.")
        raise SystemExit(1)
    print(f"OK: All {checked} images in {dest_root.name} exist in data_raw under the same class. No mislabeling introduced by the split.")


if __name__ == "__main__":
    main()

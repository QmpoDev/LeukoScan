"""
Run classify.py on the same image with both models (4000-subset and full-dataset) for comparison.
Usage: python test_both_models.py <path_to_image>
  Image path can be e.g. data_split/TEST/Eosinophil/some.jpg
"""
import sys
from pathlib import Path

# Reuse classify logic
from classify import classify_image, DEFAULT_MODEL, CLASS_LABELS

# Model filenames (must match what you have under saved_model/)
MODEL_4000 = "saved_model/blood_cell_model_4000.keras"
MODEL_FULL = "saved_model/blood_cell_model_full.keras"
# Fallback: default from classify.py (e.g. blood_cell_model.keras)
MODEL_DEFAULT = DEFAULT_MODEL


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python test_both_models.py <path_to_image>")
        sys.exit(1)
    img_path = sys.argv[1]
    if not Path(img_path).exists():
        print(f"File not found: {img_path}")
        sys.exit(1)

    models_to_try = [
        ("4000-subset", MODEL_4000),
        ("full-dataset", MODEL_FULL),
        ("default", MODEL_DEFAULT),
    ]
    # Dedupe by path so we don't run same file twice
    seen = set()
    runs = []
    for name, path in models_to_try:
        if path in seen or not Path(path).exists():
            continue
        seen.add(path)
        runs.append((name, path))

    if not runs:
        print("No model files found. Expected one of:")
        for _, p in models_to_try:
            print(f"  {p}")
        sys.exit(1)

    print(f"Image: {img_path}\n")
    for name, model_path in runs:
        try:
            label, conf = classify_image(img_path, model_path)
            print(f"[{name}] {model_path}")
            print(f"  -> {label} ({conf*100:.2f}%)\n")
        except Exception as e:
            print(f"[{name}] {model_path}")
            print(f"  -> Error: {e}\n")


if __name__ == "__main__":
    main()

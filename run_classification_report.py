"""
Run the trained model on all test-set images and save results for documentation.
Usage: python run_classification_report.py [--model NAME] [--output-dir results]
  Examples:
    python run_classification_report.py --model blood_cell_model_full.keras
    python run_classification_report.py --model blood_cell_model_4000.keras
  Default: blood_cell_model_full.keras (looked up in saved_model/).
  Each model's report is saved in a separate subdir (e.g. results/blood_cell_model_full/) so runs do not overwrite.
"""
import argparse
import csv
import os
from pathlib import Path

import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing import image

SAVED_MODEL_DIR = Path("saved_model")
DEFAULT_MODEL_NAME = "blood_cell_model_full.keras"
CLASS_LABELS = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


def main():
    parser = argparse.ArgumentParser(description="Classify all test images and save report.")
    parser.add_argument("--output-dir", default="results", help="Base dir for reports (default: results); each model gets a subdir")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME,
                        help=f"Model filename in saved_model/ (default: {DEFAULT_MODEL_NAME})")
    parser.add_argument("--data-dir", default=None,
                        help="Data root containing TEST/ (default: data_split_4000 for 4000 model, else data_split_full)")
    parser.add_argument("--tta", type=int, default=0,
                        help="Test-time augmentation: average predictions over N versions (0=off, 2=original+hflip, 4=+vflip).")
    args = parser.parse_args()
    # Infer test set: use data_split_4000 for 4000 model, data_split_full for full model
    if args.data_dir is None:
        args.data_dir = "data_split_4000" if "4000" in Path(args.model).stem else "data_split_full"
    test_dir = Path(args.data_dir) / "TEST"

    # Subdir per model so full and 4000 reports don't overwrite (e.g. results/blood_cell_model_full/)
    model_stem = Path(args.model).stem
    out_dir = Path(args.output_dir) / model_stem
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = SAVED_MODEL_DIR / args.model

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}. Run training.py or use --model blood_cell_model_4000.keras")

    # compile=False: v2 focal models save custom FocalLoss; inference only needs weights.
    model = keras.models.load_model(str(model_path), compile=False)
    # Use model input shape (e.g. 224x224 for EfficientNet 95 model, 150x150 for custom CNN)
    input_shape = model.input_shape
    image_size = (int(input_shape[1]), int(input_shape[2]))
    # EfficientNet expects [0, 255]; custom CNN expects [0, 1]
    use_0_255 = image_size[0] in (224, 260, 300)
    tta = max(0, args.tta)
    if tta:
        print(f"Using model: {model_path}, test set: {test_dir}, size={image_size}, TTA={tta}")
    else:
        print(f"Using model: {model_path}, test set: {test_dir}, size={image_size}")

    # Collect all (path, true_label)
    rows = []
    for class_name in CLASS_LABELS:
        class_dir = test_dir / class_name
        if not class_dir.exists():
            continue
        for f in class_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                rows.append((str(f), class_name))

    def predict_one(img_array: np.ndarray, use_tta: int):
        """Single image (1,H,W,3). If use_tta>0, average predictions over augmented versions."""
        if use_tta <= 0:
            p = model.predict(img_array, verbose=0)[0]
            return p
        preds = [model.predict(img_array, verbose=0)[0]]
        preds.append(model.predict(np.flip(img_array, axis=2), verbose=0)[0])  # h flip
        if use_tta >= 4:
            preds.append(model.predict(np.flip(img_array, axis=1), verbose=0)[0])  # v flip
            preds.append(model.predict(np.flip(np.flip(img_array, axis=2), axis=1), verbose=0)[0])  # both
        return np.mean(preds, axis=0)

    # Predict each image
    results = []
    for img_path, true_label in rows:
        img = image.load_img(img_path, target_size=image_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        if not use_0_255:
            img_array = img_array.astype(np.float32) / 255.0
        else:
            img_array = img_array.astype(np.float32)  # EfficientNet expects [0, 255]
        preds = predict_one(img_array, tta)
        pred_idx = int(np.argmax(preds))
        pred_label = CLASS_LABELS[pred_idx]
        confidence = float(preds[pred_idx])
        correct = 1 if pred_label == true_label else 0
        results.append({
            "image": Path(img_path).name,
            "true_class": true_label,
            "predicted_class": pred_label,
            "confidence": round(confidence, 4),
            "correct": correct,
        })

    # Write CSV
    csv_path = out_dir / "classification_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "true_class", "predicted_class", "confidence", "correct"])
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {csv_path} ({len(results)} rows)")

    # Confusion matrix
    n = len(CLASS_LABELS)
    cm = np.zeros((n, n), dtype=int)
    for r in results:
        i = CLASS_LABELS.index(r["true_class"])
        j = CLASS_LABELS.index(r["predicted_class"])
        cm[i, j] += 1
    cm_path = out_dir / "confusion_matrix.csv"
    with open(cm_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + CLASS_LABELS)
        for i, label in enumerate(CLASS_LABELS):
            w.writerow([label] + list(cm[i]))
    print(f"Wrote {cm_path}")

    # Summary
    total = len(results)
    correct_count = sum(r["correct"] for r in results)
    accuracy = correct_count / total if total else 0
    per_class = {}
    for c in CLASS_LABELS:
        subset = [r for r in results if r["true_class"] == c]
        n_c = len(subset)
        n_correct = sum(r["correct"] for r in subset)
        per_class[c] = (n_correct / n_c * 100 if n_c else 0, n_correct, n_c)

    summary_path = out_dir / "classification_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Classification report (test set)\n")
        f.write("================================\n\n")
        f.write(f"Total images: {total}\n")
        f.write(f"Correct: {correct_count}\n")
        f.write(f"Test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n\n")
        f.write("Per-class accuracy (on test set):\n")
        for c in CLASS_LABELS:
            acc_pct, n_correct, n_total = per_class[c]
            f.write(f"  {c}: {acc_pct:.2f}% ({n_correct}/{n_total})\n")
        f.write("\nConfusion matrix (rows=true, cols=predicted):\n")
        f.write("  " + ", ".join(CLASS_LABELS) + "\n")
        num_classes = len(CLASS_LABELS)
        for i, label in enumerate(CLASS_LABELS):
            f.write(f"  {label}: " + ", ".join(str(cm[i, j]) for j in range(num_classes)) + "\n")
    print(f"Wrote {summary_path}")
    print(f"\nTest accuracy: {accuracy*100:.2f}%")


if __name__ == "__main__":
    main()

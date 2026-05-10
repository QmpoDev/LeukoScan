"""
Ensemble: average predicted probabilities from multiple models, then argmax.
Often gains +1-3% over a single model.
Usage:
  python run_ensemble_report.py --models blood_cell_model_95_full.keras blood_cell_model_95_stronger_full.keras
  python run_ensemble_report.py --models model1.keras model2.keras model3.keras --tta 4 --output-dir results
All models must use the same input size (e.g. 224x224). Writes to results/ensemble_<suffix>/.
"""
import argparse
import csv
from pathlib import Path

import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing import image

SAVED_MODEL_DIR = Path("saved_model")
CLASS_LABELS = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


def main():
    parser = argparse.ArgumentParser(description="Ensemble multiple models: average probs, report accuracy.")
    parser.add_argument("--models", nargs="+", required=True, help="Model filenames in saved_model/ (e.g. blood_cell_model_95_full.keras blood_cell_model_95_stronger_full.keras)")
    parser.add_argument("--data-dir", default="data_split_full", help="Data root containing TEST/")
    parser.add_argument("--output-dir", default="results", help="Base dir for reports")
    parser.add_argument("--tta", type=int, default=0, help="TTA per model: 0=off, 2=hflip, 4=+vflip.")
    args = parser.parse_args()

    test_dir = Path(args.data_dir) / "TEST"
    model_paths = [SAVED_MODEL_DIR / m for m in args.models]
    for p in model_paths:
        if not p.exists():
            raise FileNotFoundError(f"Model not found: {p}")

    models = []
    image_size = None
    use_0_255 = None
    for p in model_paths:
        m = keras.models.load_model(str(p), compile=False)
        models.append(m)
        shp = m.input_shape
        sz = (int(shp[1]), int(shp[2]))
        if image_size is None:
            image_size = sz
            use_0_255 = image_size[0] in (224, 260, 300)
        elif sz != image_size:
            raise ValueError(f"All models must have same input size. First has {image_size}, {p.name} has {sz}.")

    tta = max(0, args.tta)
    stems = "_".join(Path(m).stem for m in args.models)
    # Include TTA in folder name so e.g. TTA=0 and TTA=4 runs do not overwrite the same results dir.
    ensemble_name = f"ensemble_{stems[:55]}_tta{tta}"
    out_dir = Path(args.output_dir) / ensemble_name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Ensemble of {len(models)} models, test set: {test_dir}, size={image_size}, TTA={tta}")

    rows = []
    for class_name in CLASS_LABELS:
        class_dir = test_dir / class_name
        if not class_dir.exists():
            continue
        for f in class_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                rows.append((str(f), class_name))

    def predict_one_image(img_array: np.ndarray):
        """Average probabilities over all models and optional TTA."""
        all_probs = []
        for model in models:
            if tta <= 0:
                p = model.predict(img_array, verbose=0)[0]
                all_probs.append(p)
            else:
                preds = [model.predict(img_array, verbose=0)[0]]
                preds.append(model.predict(np.flip(img_array, axis=2), verbose=0)[0])
                if tta >= 4:
                    preds.append(model.predict(np.flip(img_array, axis=1), verbose=0)[0])
                    preds.append(model.predict(np.flip(np.flip(img_array, axis=2), axis=1), verbose=0)[0])
                all_probs.append(np.mean(preds, axis=0))
        return np.mean(all_probs, axis=0)

    results = []
    for img_path, true_label in rows:
        img = image.load_img(img_path, target_size=image_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        if not use_0_255:
            img_array = img_array.astype(np.float32) / 255.0
        else:
            img_array = img_array.astype(np.float32)
        probs = predict_one_image(img_array)
        pred_idx = int(np.argmax(probs))
        pred_label = CLASS_LABELS[pred_idx]
        confidence = float(probs[pred_idx])
        correct = 1 if pred_label == true_label else 0
        results.append({
            "image": Path(img_path).name,
            "true_class": true_label,
            "predicted_class": pred_label,
            "confidence": round(confidence, 4),
            "correct": correct,
        })

    csv_path = out_dir / "classification_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "true_class", "predicted_class", "confidence", "correct"])
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {csv_path} ({len(results)} rows)")

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
        f.write("Ensemble classification report (test set)\n")
        f.write("=========================================\n\n")
        f.write(f"Models: {args.models}\n")
        f.write(f"TTA: {tta}\n\n")
        f.write(f"Total images: {total}\n")
        f.write(f"Correct: {correct_count}\n")
        f.write(f"Test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n\n")
        f.write("Per-class accuracy (on test set):\n")
        for c in CLASS_LABELS:
            acc_pct, n_correct, n_total = per_class[c]
            f.write(f"  {c}: {acc_pct:.2f}% ({n_correct}/{n_total})\n")
        f.write("\nConfusion matrix (rows=true, cols=predicted):\n")
        f.write("  " + ", ".join(CLASS_LABELS) + "\n")
        for i, label in enumerate(CLASS_LABELS):
            f.write(f"  {label}: " + ", ".join(str(cm[i, j]) for j in range(n)) + "\n")
    print(f"Wrote {summary_path}")
    print(f"\nEnsemble test accuracy: {accuracy*100:.2f}%")


if __name__ == "__main__":
    main()

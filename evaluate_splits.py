"""
Evaluate the same model on TRAIN, VAL, and TEST with identical preprocessing.

This gives comparable numbers across splits. Augmentation and dropout are off
(Keras eval mode), so this is not the same as noisy batch accuracy during fit().

After prepare_data.py (current layout), TRAIN is from original TRAIN only; VAL and
TEST are disjoint halves of original TEST. Use the same preprocessing for all three
when comparing metrics.
"""

import argparse
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras import optimizers
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

DEFAULT_SPLITS = ("TRAIN", "VAL", "TEST")


def make_datagen(model_path: str, rescale_mode: str):
    model_name = Path(model_path).stem.lower()
    if rescale_mode == "auto":
        use_rescale = not any(
            k in model_name for k in ("95", "efficientnet", "_b0_", "_b1_", "_b3_", "v2_")
        )
    else:
        use_rescale = rescale_mode == "1/255"

    if use_rescale:
        return ImageDataGenerator(rescale=1.0 / 255.0), "rescale=1/255"
    return ImageDataGenerator(), "no rescale (pixel range [0,255])"


def run_split(
    model,
    split_dir: Path,
    img_size: tuple[int, int],
    batch_size: int,
    datagen: ImageDataGenerator,
    detailed: bool,
    split_label: str,
) -> None:
    if not split_dir.is_dir():
        print(f"\n=== {split_label} ===\nSkip: folder not found: {split_dir}")
        return

    gen = datagen.flow_from_directory(
        str(split_dir),
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
    )
    print(f"\n=== {split_label} ({gen.samples} images) ===")
    loss, accuracy = model.evaluate(gen, verbose=1)
    print(f"{split_label} Loss: {loss}")
    print(f"{split_label} Accuracy: {accuracy}")

    if not detailed:
        return

    predictions = model.predict(gen, verbose=1)
    y_pred = np.argmax(predictions, axis=1)
    y_true = gen.classes
    class_labels = list(gen.class_indices.keys())

    cm = confusion_matrix(y_true, y_pred)
    print(f"\n{split_label} Confusion Matrix:")
    print(cm)
    report = classification_report(y_true, y_pred, target_names=class_labels)
    print(f"\n{split_label} Classification Report:")
    print(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate model on TRAIN, VAL, and TEST with the same preprocessing."
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="saved_model/blood_cell_model_95_full.keras",
        help="Path to a .keras model file.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data_split_full",
        help="Data root containing TRAIN/, VAL/, TEST/ class subfolders.",
    )
    parser.add_argument(
        "--img-size",
        type=int,
        nargs=2,
        default=(224, 224),
        metavar=("HEIGHT", "WIDTH"),
        help="Target size (must match training for this model).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--rescale-mode",
        choices=["auto", "none", "1/255"],
        default="auto",
        help="Input scaling: auto (from model filename), none, or 1/255.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=list(DEFAULT_SPLITS),
        help="Split folder names under data-dir (default: TRAIN VAL TEST).",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Also print confusion matrix and classification report per split.",
    )
    args = parser.parse_args()

    model = load_model(args.model_path, compile=False)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    datagen, preproc_desc = make_datagen(args.model_path, args.rescale_mode)
    print(f"Model: {args.model_path}")
    print(f"Data dir: {args.data_dir}")
    print(f"Preprocessing: {preproc_desc}")

    data_root = Path(args.data_dir)
    img_size = tuple(args.img_size)

    for name in args.splits:
        run_split(
            model,
            data_root / name,
            img_size,
            args.batch_size,
            datagen,
            args.detailed,
            name,
        )


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras import optimizers
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a trained Keras model on a validation folder."
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="saved_model/blood_cell_model_95_full_run1.keras",
        help="Path to a .keras model file.",
    )
    parser.add_argument(
        "--validation-dir",
        type=str,
        default="data_split_full/VAL",
        help="Validation directory with one subfolder per class.",
    )
    parser.add_argument(
        "--img-size",
        type=int,
        nargs=2,
        default=(224, 224),
        metavar=("HEIGHT", "WIDTH"),
        help="Target image size used for evaluation.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for validation loading.",
    )
    parser.add_argument(
        "--rescale-mode",
        choices=["auto", "none", "1/255"],
        default="auto",
        help="Input scaling: auto (based on model), none, or 1/255.",
    )
    args = parser.parse_args()

    model = load_model(args.model_path, compile=False)
    # Focal-loss checkpoints omit custom loss unless imported; recompile for evaluate() only.
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    model_name = Path(args.model_path).stem.lower()
    # In this repo, EfficientNet transfer models (95/v2/B0/B1/B3) were trained on [0,255].
    if args.rescale_mode == "auto":
        use_rescale = not any(
            k in model_name for k in ("95", "efficientnet", "_b0_", "_b1_", "_b3_", "v2_")
        )
    else:
        use_rescale = args.rescale_mode == "1/255"

    if use_rescale:
        print("Preprocessing: rescale=1/255")
        val_datagen = ImageDataGenerator(rescale=1.0 / 255.0)
    else:
        print("Preprocessing: no rescale (pixel range [0,255])")
        val_datagen = ImageDataGenerator()
    val_generator = val_datagen.flow_from_directory(
        args.validation_dir,
        target_size=tuple(args.img_size),
        batch_size=args.batch_size,
        class_mode="categorical",
        shuffle=False,
    )

    loss, accuracy = model.evaluate(val_generator, verbose=1)
    print("\nValidation Loss:", loss)
    print("Validation Accuracy:", accuracy)

    predictions = model.predict(val_generator, verbose=1)
    y_pred = np.argmax(predictions, axis=1)
    y_true = val_generator.classes
    class_labels = list(val_generator.class_indices.keys())

    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    report = classification_report(y_true, y_pred, target_names=class_labels)
    print("\nClassification Report:")
    print(report)


if __name__ == "__main__":
    main()

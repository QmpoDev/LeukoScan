"""
Classify a single blood cell image using a trained model.

Usage:
  python classify.py <path_to_image> [path_to_model.keras]

  If no image path is given, the script prompts for it.
  Optional second argument = which model to use (default: full-dataset model).

Examples:
  python classify.py data_split_full/TEST/Eosinophil/_0_1414.jpeg
  python classify.py my_image.jpg saved_model/blood_cell_model_full.keras
  python classify.py my_image.jpg saved_model/blood_cell_model_4000.keras

Classes: Eosinophil, Lymphocyte, Monocyte, Neutrophil.
Image is resized to 150x150 and normalized to [0, 1]; output is predicted class and confidence.
"""
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

DEFAULT_MODEL = "saved_model/blood_cell_model_full.keras"
IMAGE_SIZE = (150, 150)
# Class order matches image_dataset_from_directory (alphabetical folder names)
CLASS_LABELS = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

# ---------------------------------------------------------------------------
# Model singleton cache — avoids reloading from disk on every request.
# Keys are absolute model paths; values are loaded tf.keras.Model objects.
# ---------------------------------------------------------------------------
_MODEL_CACHE: dict = {}


def _load_model(path: str):
    """Return a cached model, loading from disk only on first call per path."""
    if path not in _MODEL_CACHE:
        _MODEL_CACHE[path] = tf.keras.models.load_model(path, compile=False)
    return _MODEL_CACHE[path]


def classify_image(img_path: str, model_path: str = None) -> tuple:
    """
    Classify a single blood cell image.

    Args:
        img_path:   Path to a JPEG or PNG image file.
        model_path: Path to a .keras model file. Defaults to DEFAULT_MODEL.

    Returns:
        (predicted_label: str, confidence: float)
        predicted_label is one of CLASS_LABELS.
        confidence is a float in [0.0, 1.0].

    Raises:
        PIL.UnidentifiedImageError: if the image file cannot be decoded.
        FileNotFoundError: if the model file does not exist.
        Exception: for any other inference error.
    """
    path = model_path or DEFAULT_MODEL
    model = _load_model(path)

    img = image.load_img(img_path, target_size=IMAGE_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # normalize to [0, 1]

    predictions = model.predict(img_array, verbose=0)
    predicted_class = int(np.argmax(predictions[0]))
    predicted_label = CLASS_LABELS[predicted_class]
    confidence = float(predictions[0][predicted_class])
    return predicted_label, confidence


def main() -> None:
    if len(sys.argv) >= 2:
        img_path = sys.argv[1]
    else:
        img_path = input("Enter image path: ").strip()
    model_path = sys.argv[2] if len(sys.argv) >= 3 else None

    if not img_path:
        print("No image path provided.")
        sys.exit(1)

    path = model_path or DEFAULT_MODEL
    print(f"Model: {path}")
    label, conf = classify_image(img_path, model_path)
    print("Predicted class:", label)
    print("Confidence: {:.2f}%".format(conf * 100))


if __name__ == "__main__":
    main()

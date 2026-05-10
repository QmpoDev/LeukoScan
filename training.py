"""
Train blood cell classifier with:
- Class weights for imbalanced classes (e.g. Eosinophil)
- BatchNorm, L2 regularization, Dense(256) to reduce overfitting
- ReduceLROnPlateau + EarlyStopping, label smoothing
- Training-time augmentation (flip, rotation, zoom, Gaussian noise)
"""
import argparse
import os
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Log GPU availability (TensorFlow uses GPU automatically if available)
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print(f"Using GPU: {[gpu.name for gpu in gpus]}")
else:
    print("No GPU found. Training on CPU. See docs/GPU_SETUP.md for GPU options on Windows.")

# Step 1: Paths and config
parser = argparse.ArgumentParser(description="Train blood cell classifier on a given data split.")
parser.add_argument("--data-dir", default="data_split_full", help="Data root (e.g. data_split_4000 or data_split_full)")
args = parser.parse_args()

data_dir = args.data_dir
train_dir = os.path.join(data_dir, "TRAIN")
val_dir = os.path.join(data_dir, "VAL")
test_dir = os.path.join(data_dir, "TEST")
batch_size = 32
image_size = (150, 150)
# Tuning: high patience so training can reach plateau (early stop was cutting off too soon)
EARLY_STOP_PATIENCE = 32
LEARNING_RATE = 1e-4
REDUCE_LR_PATIENCE = 10
num_classes = 4
CLASS_NAMES = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]  # alphabetical
L2_REG = 3e-5
LABEL_SMOOTHING = 0.01


def _count_images(dir_path: str) -> int:
    p = Path(dir_path)
    if not p.exists():
        return 0
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    return sum(1 for f in p.rglob("*") if f.is_file() and f.suffix.lower() in exts)


def get_class_weights(train_dir: str) -> dict[int, float]:
    """Compute class weights for imbalanced classes (inverse frequency)."""
    counts = []
    for c in CLASS_NAMES:
        counts.append(_count_images(os.path.join(train_dir, c)))
    total = sum(counts)
    n = num_classes
    # weight_i = total / (n * count_i) so that weighted count is balanced
    weights = {i: total / (n * (counts[i] or 1)) for i in range(n)}
    return weights


# Step 2: Datasets
train_ds = keras.utils.image_dataset_from_directory(
    train_dir,
    image_size=image_size,
    batch_size=batch_size,
    label_mode="categorical",
    shuffle=True,
    seed=42,
)
val_ds = keras.utils.image_dataset_from_directory(
    val_dir,
    image_size=image_size,
    batch_size=batch_size,
    label_mode="categorical",
    shuffle=False,
)
test_ds = keras.utils.image_dataset_from_directory(
    test_dir,
    image_size=image_size,
    batch_size=batch_size,
    label_mode="categorical",
    shuffle=False,
)

# Normalize to [0, 1]
normalize = lambda img, label: (img / 255.0, label)

# Augmentation layers created once (cannot create Keras layers inside dataset.map — tf.function).
augment_layers = keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.05, fill_mode="reflect"),
])


def augment(img, label):
    """Training-time augmentation: flips, rotation, zoom, Gaussian noise. img is a batch (B,H,W,C)."""
    img = tf.cast(img, tf.float32) / 255.0
    img = augment_layers(img, training=True)
    img = img + tf.random.normal(tf.shape(img), stddev=0.01)
    img = tf.clip_by_value(img, 0.0, 1.0)
    return img, label


train_ds = train_ds.map(augment).repeat()
val_ds = val_ds.map(normalize)
test_ds = test_ds.map(normalize)

# Class weights for underperforming classes (e.g. Eosinophil)
class_weight = get_class_weights(train_dir)

# Step 3: Model — BatchNorm after Conv2D, L2 reg, Dense(256)
reg = keras.regularizers.l2(L2_REG)
model = keras.Sequential([
    layers.Input(shape=(*image_size, 3)),
    layers.Conv2D(32, (3, 3), activation="relu", kernel_regularizer=reg),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation="relu", kernel_regularizer=reg),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation="relu", kernel_regularizer=reg),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation="relu", kernel_regularizer=reg),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dropout(0.25),
    layers.Dense(256, activation="relu", kernel_regularizer=reg),
    layers.Dropout(0.35),
    layers.Dense(num_classes, activation="softmax"),
])

# Step 4: Compile — label smoothing to reduce overconfidence
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss=keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
    metrics=["accuracy"],
)

# Step 5: Train — EarlyStopping + ReduceLROnPlateau
train_samples = _count_images(train_dir)
val_samples = _count_images(val_dir)
steps_per_epoch = train_samples // batch_size
validation_steps = max(1, val_samples // batch_size)
if train_samples == 0 or val_samples == 0:
    raise RuntimeError(f"No images in {train_dir} or {val_dir}. Run prepare_data.py first.")

early_stop = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=EARLY_STOP_PATIENCE,
    restore_best_weights=True,
    verbose=1,
)
reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=REDUCE_LR_PATIENCE,
    min_lr=1e-6,
    verbose=1,
)

history = model.fit(
    train_ds,
    steps_per_epoch=steps_per_epoch,
    epochs=50,
    validation_data=val_ds,
    validation_steps=validation_steps,
    class_weight=class_weight,
    callbacks=[early_stop, reduce_lr],
)

# Step 6: Evaluate
test_loss, test_acc = model.evaluate(test_ds, verbose=2)
print("\nTest accuracy:", test_acc)

# Step 7: Save
directory = "saved_model"
os.makedirs(directory, exist_ok=True)
model_name = "blood_cell_model_4000.keras" if "4000" in data_dir else "blood_cell_model_full.keras"
model.save(os.path.join(directory, model_name))
print(f"Model saved to {directory}/{model_name}.")

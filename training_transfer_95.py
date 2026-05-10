"""
Transfer learning targeting ≥95% test accuracy (medical use).
- Backbone: EfficientNetB0/B1/B3 (ImageNet pretrained); B3 uses 300×300 input.
- Two-phase: (1) freeze base, train head only; (2) unfreeze, low LR fine-tune.
- Class weights, label smoothing, L2, dropout, moderate augmentation.
Run: python training_transfer_95.py [--data-dir data_split_full]
Saves: saved_model/blood_cell_model_95_full.keras (baseline path; existing file is not overwritten)
       or saved_model/blood_cell_model_v2_*.keras when --focal or --backbone B3 is used.
"""
import argparse
import os
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB0, EfficientNetB1, EfficientNetB3

gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print(f"Using GPU: {[gpu.name for gpu in gpus]}")
else:
    print("No GPU found. Training on CPU. See docs/GPU_SETUP.md for GPU options.")

CLASS_NAMES = ["Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]
num_classes = 4

# Target 95%: stronger backbone, larger input, two-phase fine-tune (IMAGE_SIZE set from args)
DEFAULT_IMAGE_SIZE = (224, 224)
IMAGE_SIZE = DEFAULT_IMAGE_SIZE
# Default 32 for B0/B1; B3 @ 300×300 needs a smaller batch on typical 4–8GB GPUs (override with --batch-size).
DEFAULT_BATCH_SIZE = 32
DEFAULT_BATCH_SIZE_B3 = 8
BATCH_SIZE = DEFAULT_BATCH_SIZE
L2_HEAD = 5e-5
LABEL_SMOOTHING = 0.05
HEAD_DROPOUT = 0.4
PHASE1_EPOCHS = 10
PHASE1_LR = 1e-3
PHASE2_EPOCHS = 70
PHASE2_LR = 1e-5
EARLY_STOP_PATIENCE = 20
REDUCE_LR_PATIENCE = 8
REDUCE_LR_FACTOR = 0.5
MIN_LR = 1e-7

BASELINE_PROTECTED_NAME = "blood_cell_model_95_full.keras"


def _count_images(dir_path: str) -> int:
    p = Path(dir_path)
    if not p.exists():
        return 0
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    return sum(1 for f in p.rglob("*") if f.is_file() and f.suffix.lower() in exts)


def get_class_weights(train_dir: str, boost_monocyte: bool = False) -> dict:
    counts = [_count_images(os.path.join(train_dir, c)) for c in CLASS_NAMES]
    total = sum(counts)
    n = len(CLASS_NAMES)
    weights = {i: total / (n * (counts[i] or 1)) for i in range(n)}
    if boost_monocyte:
        mi = CLASS_NAMES.index("Monocyte")
        mono_c = max(counts[mi], 1)
        sorted_c = sorted(max(c, 1) for c in counts)
        median_c = sorted_c[len(sorted_c) // 2]
        # Rarer than median → stronger upweight from actual TRAIN counts
        rarity = median_c / mono_c
        weights[mi] *= max(rarity, 1.0)
    return weights


@tf.keras.utils.register_keras_serializable(package="bloodcell")
class FocalLoss(keras.losses.Loss):
    """Multi-class focal loss with optional label smoothing on one-hot targets."""

    def __init__(self, alpha=0.25, gamma=2.0, label_smoothing=0.0, **kwargs):
        super().__init__(**kwargs)
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.label_smoothing = float(label_smoothing)

    def call(self, y_true, y_pred):
        eps = 1e-7
        y_pred = tf.clip_by_value(y_pred, eps, 1.0 - eps)
        if self.label_smoothing > 0.0:
            y_true = y_true * (1.0 - self.label_smoothing) + self.label_smoothing / float(
                num_classes
            )
        pt = tf.reduce_sum(y_true * y_pred, axis=-1)
        ce = -tf.reduce_sum(y_true * tf.math.log(y_pred), axis=-1)
        focal_weight = self.alpha * tf.pow(1.0 - pt, self.gamma)
        return tf.reduce_mean(focal_weight * ce)

    def get_config(self):
        cfg = super().get_config()
        cfg.update(
            {
                "alpha": self.alpha,
                "gamma": self.gamma,
                "label_smoothing": self.label_smoothing,
            }
        )
        return cfg


parser = argparse.ArgumentParser(description="Train blood cell classifier for ≥95% (EfficientNet, two-phase).")
parser.add_argument("--data-dir", default="data_split_full", help="Data root (data_split_4000 or data_split_full)")
parser.add_argument("--stronger", action="store_true", help="Stronger regularization (more dropout, augmentation) to improve test generalization.")
parser.add_argument("--backbone", choices=["B0", "B1", "B3"], default="B0", help="EfficientNet backbone (B1/B3 = more capacity; B3 uses 300×300).")
parser.add_argument(
    "--size",
    type=int,
    choices=[224, 260, 300],
    default=None,
    help="Input size. Default: 224 for B0, 260 for B1, 300 for B3 (B3 ignores this and always uses 300).",
)
parser.add_argument(
    "--boost-weak",
    action="store_true",
    help="Extra class weight for Monocyte from actual TRAIN folder counts (rarer → higher weight).",
)
parser.add_argument("--focal", action="store_true", help="Use focal loss (alpha=0.25, gamma=2) instead of categorical crossentropy.")
parser.add_argument(
    "--batch-size",
    type=int,
    default=None,
    metavar="N",
    help=f"Minibatch size. Default: {DEFAULT_BATCH_SIZE} for B0/B1, {DEFAULT_BATCH_SIZE_B3} for B3 (saves VRAM at 300×300).",
)
parser.add_argument("--run-id", type=int, default=None, help="Optional run number (1,2,3,...). Saves as ..._runN.keras so you can keep multiple runs for ensembling.")
args = parser.parse_args()

# Different run-id → different shuffle seed so ensemble members are not identical
# (dataset order + TF RNG). Val/test stay reproducible for a given run-id.
_train_seed = 42 if args.run_id is None else 42 + int(args.run_id) * 10_007
tf.keras.utils.set_random_seed(_train_seed)

data_dir = args.data_dir
# B3 always uses 300×300 (official EfficientNet-B3 preset). Otherwise: explicit --size wins; else 260 for B1, 224 for B0.
if args.backbone == "B3":
    IMAGE_SIZE = (300, 300)
elif args.size is not None:
    IMAGE_SIZE = (args.size, args.size)
else:
    IMAGE_SIZE = (260, 260) if args.backbone == "B1" else (224, 224)

if args.batch_size is not None:
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least 1.")
    BATCH_SIZE = args.batch_size
elif args.backbone == "B3":
    BATCH_SIZE = DEFAULT_BATCH_SIZE_B3
else:
    BATCH_SIZE = DEFAULT_BATCH_SIZE

if gpus:
    print(
        f"Batch size {BATCH_SIZE} (input {IMAGE_SIZE[0]}×{IMAGE_SIZE[1]}, backbone {args.backbone}). "
        "If you see GPU OOM, rerun with a smaller --batch-size (e.g. 4) or set TF_GPU_ALLOCATOR=cuda_malloc_async."
    )

if args.stronger:
    HEAD_DROPOUT = 0.5
    LABEL_SMOOTHING = 0.08
aug_rotation = 0.12 if args.stronger else 0.10
aug_zoom = 0.10 if args.stronger else 0.08
train_dir = os.path.join(data_dir, "TRAIN")
val_dir = os.path.join(data_dir, "VAL")
test_dir = os.path.join(data_dir, "TEST")

train_ds = keras.utils.image_dataset_from_directory(
    train_dir,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=True,
    seed=_train_seed,
)
val_ds = keras.utils.image_dataset_from_directory(
    val_dir,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False,
)
test_ds = keras.utils.image_dataset_from_directory(
    test_dir,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False,
)

# EfficientNetB0 expects inputs in [0, 255] (it has built-in Rescaling(1/255)). Do NOT pass [0,1] or activations become tiny and the model won't learn.
normalize = lambda img, label: (tf.cast(img, tf.float32), label)

# Augment in [0,1] then scale back to [0,255] for the model (size matches IMAGE_SIZE via layer)
augment_layers = keras.Sequential(
    [
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(aug_rotation),
        layers.RandomZoom(aug_zoom, fill_mode="reflect"),
        layers.RandomBrightness(0.2, value_range=(0.0, 1.0)),
        layers.RandomContrast(0.2, value_range=(0.0, 1.0)),
    ],
    name="data_augmentation",
)


def augment(img, label):
    img = tf.cast(img, tf.float32) / 255.0
    img = augment_layers(img, training=True)
    img = img + tf.random.normal(tf.shape(img), stddev=0.02)
    img = tf.clip_by_value(img, 0.0, 1.0)
    img = img * 255.0  # EfficientNet expects [0, 255]
    return img, label


train_ds = train_ds.map(augment).repeat()
val_ds = val_ds.map(normalize)
test_ds = test_ds.map(normalize)

class_weight = get_class_weights(train_dir, boost_monocyte=args.boost_weak)

loss_fn = (
    FocalLoss(alpha=0.25, gamma=2.0, label_smoothing=0.0)
    if args.focal
    else keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING)
)

train_samples = _count_images(train_dir)
val_samples = _count_images(val_dir)
steps_per_epoch = train_samples // BATCH_SIZE
validation_steps = max(1, val_samples // BATCH_SIZE)
if train_samples == 0 or val_samples == 0:
    raise RuntimeError(f"No images in {train_dir} or {val_dir}. Run prepare_data.py first.")

# Backbone: EfficientNetB0, B1, or B3, ImageNet weights
if args.backbone == "B3":
    EfficientNetBackbone = EfficientNetB3
elif args.backbone == "B1":
    EfficientNetBackbone = EfficientNetB1
else:
    EfficientNetBackbone = EfficientNetB0

base = EfficientNetBackbone(
    input_shape=(*IMAGE_SIZE, 3),
    include_top=False,
    weights="imagenet",
    pooling="avg",
)
reg = keras.regularizers.l2(L2_HEAD)
classifier = keras.Sequential([
    layers.Dropout(HEAD_DROPOUT),
    layers.Dense(256, activation="relu", kernel_regularizer=reg),
    layers.Dropout(HEAD_DROPOUT),
    layers.Dense(num_classes, activation="softmax"),
])
model = keras.Sequential([base, classifier])

# Phase 1: freeze backbone, train head only
base.trainable = False
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=PHASE1_LR),
    loss=loss_fn,
    metrics=["accuracy"],
)
print("Phase 1: training head only (base frozen)...")
model.fit(
    train_ds,
    steps_per_epoch=steps_per_epoch,
    epochs=PHASE1_EPOCHS,
    validation_data=val_ds,
    validation_steps=validation_steps,
    class_weight=class_weight,
)

# Phase 2: unfreeze backbone but keep BatchNorm frozen (avoids val_loss spikes / instability)
base.trainable = True
for layer in base.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False
# Gradient clipping to prevent exploding logits (val_loss was 300+ otherwise)
optimizer = keras.optimizers.Adam(learning_rate=PHASE2_LR, clipnorm=1.0)
model.compile(
    optimizer=optimizer,
    loss=loss_fn,
    metrics=["accuracy"],
)
early_stop = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=EARLY_STOP_PATIENCE,
    restore_best_weights=True,
    verbose=1,
)
reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss",
    factor=REDUCE_LR_FACTOR,
    patience=REDUCE_LR_PATIENCE,
    min_lr=MIN_LR,
    verbose=1,
)
print("Phase 2: fine-tuning full model (low LR)...")
model.fit(
    train_ds,
    steps_per_epoch=steps_per_epoch,
    epochs=PHASE2_EPOCHS,
    validation_data=val_ds,
    validation_steps=validation_steps,
    class_weight=class_weight,
    callbacks=[early_stop, reduce_lr],
)

test_loss, test_acc = model.evaluate(test_ds, verbose=2)
print("\nTest accuracy:", test_acc)

os.makedirs("saved_model", exist_ok=True)
suffix = "4000" if "4000" in data_dir else "full"

uses_v2 = args.focal or args.backbone == "B3"

if uses_v2:
    name_parts = ["blood_cell_model", "v2"]
    if args.backbone == "B3":
        name_parts.append("B3")
    if args.focal:
        name_parts.append("focal")
    if args.stronger:
        name_parts.append("stronger")
    if args.boost_weak:
        name_parts.append("boostweak")
    if args.backbone != "B3" and (args.backbone != "B0" or IMAGE_SIZE[0] != 224):
        name_parts.append(f"{args.backbone}_{IMAGE_SIZE[0]}")
    name_parts.append(suffix)
    if args.run_id is not None:
        name_parts.append(f"run{args.run_id}")
    model_name = "_".join(name_parts) + ".keras"
else:
    name_parts = ["blood_cell_model_95"]
    if args.stronger:
        name_parts.append("stronger")
    if args.boost_weak:
        name_parts.append("boostweak")
    if args.backbone != "B0" or IMAGE_SIZE[0] != 224:
        name_parts.append(f"{args.backbone}_{IMAGE_SIZE[0]}")
    name_parts.append(suffix)
    if args.run_id is not None:
        name_parts.append(f"run{args.run_id}")
    model_name = "_".join(name_parts) + ".keras"

save_path = os.path.join("saved_model", model_name)
if model_name == BASELINE_PROTECTED_NAME and os.path.isfile(save_path):
    n = 1
    while True:
        alt = f"blood_cell_model_95_full_alt{n}.keras"
        alt_path = os.path.join("saved_model", alt)
        if not os.path.isfile(alt_path):
            model_name = alt
            save_path = alt_path
            print(
                f"Refusing to overwrite {BASELINE_PROTECTED_NAME}; saving as saved_model/{model_name} instead."
            )
            break
        n += 1

model.save(save_path)
print(f"Model saved to {save_path}.")
print("Run: python run_classification_report.py --model", model_name)

#!/usr/bin/env bash
set -e
set -u
set -o pipefail

# End-to-end run: prepare full split, train 4 diverse models, run reports, run ensemble.
# Run from repo root in your training environment (WSL recommended).

PYTHON="${PYTHON:-python}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON="python3"
fi

DATA_DIR="${DATA_DIR:-data_split_full}"
TTA="${TTA:-4}"

echo "==> Using interpreter: $PYTHON"

echo "==> Preparing data split (full)"
$PYTHON prepare_data.py --full

echo "==> Training Model A: B0 224"
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B0 --size 224

echo "==> Training Model B: B0 224 stronger"
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B0 --size 224 --stronger

echo "==> Training Model C: B1 224"
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B1 --size 224

echo "==> Training Model D: B1 224 stronger + boost weak classes"
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B1 --size 224 --stronger --boost-weak

MODEL_A="blood_cell_model_95_full.keras"
MODEL_B="blood_cell_model_95_stronger_full.keras"
MODEL_C="blood_cell_model_95_B1_224_full.keras"
MODEL_D="blood_cell_model_95_stronger_boostweak_B1_224_full.keras"

echo "==> Running per-model reports (TTA=$TTA)"
$PYTHON run_classification_report.py --model "$MODEL_A" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_B" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_C" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_D" --data-dir "$DATA_DIR" --tta "$TTA"

echo "==> Running ensemble (TTA=$TTA)"
$PYTHON run_ensemble_report.py --models "$MODEL_A" "$MODEL_B" "$MODEL_C" "$MODEL_D" --tta "$TTA" --data-dir "$DATA_DIR"

echo
echo "Done."
echo "Per-model results: results/<model_stem>/classification_summary.txt"
echo "Ensemble results:  results/ensemble_*/classification_summary.txt"

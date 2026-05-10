#!/usr/bin/env bash
set -e
set -u
set -o pipefail

# Run only the 4 per-model reports + ensemble. Use this after you have all 4 models
# (e.g. you cancelled run_all_95.sh and later trained Model D by hand).
# Convert CRLF first if needed: sed -i 's/\r$//' run_reports_and_ensemble_only.sh

PYTHON="${PYTHON:-python}"
DATA_DIR="${DATA_DIR:-data_split_full}"
TTA="${TTA:-4}"

MODEL_A="blood_cell_model_95_full.keras"
MODEL_B="blood_cell_model_95_stronger_full.keras"
MODEL_C="blood_cell_model_95_B1_224_full.keras"
MODEL_D="blood_cell_model_95_stronger_boostweak_B1_224_full.keras"

for m in "$MODEL_A" "$MODEL_B" "$MODEL_C" "$MODEL_D"; do
  if [ ! -f "saved_model/$m" ]; then
    echo "Missing saved_model/$m - train it first, then run this script."
    exit 1
  fi
done

echo "==> Running per-model reports (TTA=$TTA)"
$PYTHON run_classification_report.py --model "$MODEL_A" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_B" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_C" --data-dir "$DATA_DIR" --tta "$TTA"
$PYTHON run_classification_report.py --model "$MODEL_D" --data-dir "$DATA_DIR" --tta "$TTA"

echo "==> Running ensemble (TTA=$TTA)"
$PYTHON run_ensemble_report.py --models "$MODEL_A" "$MODEL_B" "$MODEL_C" "$MODEL_D" --tta "$TTA" --data-dir "$DATA_DIR"

echo
echo "Done. Ensemble result: results/ensemble_*/classification_summary.txt"

#!/usr/bin/env bash
# Push test accuracy on the honest split (TRAIN-only / TEST-halves val+test).
# Run from project root (WSL/Linux). Uses PYTHON if set, else python3.
#
# 1) Quick: TTA=4 on your existing 3 default B0 runs (no retraining).
# 2) Long: train 3x --stronger with distinct run seeds, then ensemble + TTA=4.
#
# Optional 4th block: 6-model ensemble (default + stronger), TTA=4 — slow at inference.
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
DATA_DIR="${DATA_DIR:-data_split_full}"

M1=blood_cell_model_95_full_run1.keras
M2=blood_cell_model_95_full_run2.keras
M3=blood_cell_model_95_full_run3.keras
S1=blood_cell_model_95_stronger_full_run1.keras
S2=blood_cell_model_95_stronger_full_run2.keras
S3=blood_cell_model_95_stronger_full_run3.keras

echo "=== A) Existing 3 runs — ensemble with TTA=4 (try this first) ==="
$PYTHON run_ensemble_report.py --models "$M1" "$M2" "$M3" --data-dir "$DATA_DIR" --tta 4

echo ""
echo "=== B) Train 3x stronger B0 (same as default but more aug + dropout) ==="
for i in 1 2 3; do
  $PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --stronger --run-id "$i"
done

echo ""
echo "=== C) Ensemble stronger x3 + TTA=4 ==="
$PYTHON run_ensemble_report.py --models "$S1" "$S2" "$S3" --data-dir "$DATA_DIR" --tta 4

echo ""
echo "=== D) Optional: 6-model ensemble + TTA=4 (slow; may or may not beat C) ==="
$PYTHON run_ensemble_report.py \
  --models "$M1" "$M2" "$M3" "$S1" "$S2" "$S3" \
  --data-dir "$DATA_DIR" \
  --tta 4

echo ""
echo "Done. Compare results/ensemble_*/classification_summary.txt (newest dirs at bottom of ls -lt results)."

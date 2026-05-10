#!/bin/bash
# Reach ~90%: train 3 B0 224 runs (different seeds), then ensemble them.
# Run from project root. Needs: prepare_data.py --full already done.
set -e
PYTHON=${PYTHON:-python3}
DATA_DIR=${DATA_DIR:-data_split_full}

echo "Training 3 B0 224 runs..."
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B0 --size 224 --run-id 1
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B0 --size 224 --run-id 2
$PYTHON training_transfer_95.py --data-dir "$DATA_DIR" --backbone B0 --size 224 --run-id 3

echo "Running reports (TTA=4) on each run..."
for i in 1 2 3; do
  $PYTHON run_classification_report.py --model saved_model/blood_cell_model_95_full_run${i}.keras --data-dir "$DATA_DIR" --tta 4
done

echo "Ensembling 3 runs..."
$PYTHON run_ensemble_report.py --models blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras --data-dir "$DATA_DIR" --tta 4

echo "Done. Check results/ensemble_*/classification_summary.txt for test accuracy."

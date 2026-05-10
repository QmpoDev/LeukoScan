@echo off
REM Reach ~90%%: train 3 B0 224 runs, then ensemble. Run from project root.
set DATA_DIR=data_split_full

echo Training 3 B0 224 runs...
python training_transfer_95.py --data-dir %DATA_DIR% --backbone B0 --size 224 --run-id 1
python training_transfer_95.py --data-dir %DATA_DIR% --backbone B0 --size 224 --run-id 2
python training_transfer_95.py --data-dir %DATA_DIR% --backbone B0 --size 224 --run-id 3

echo Running reports (TTA=4) on each run...
python run_classification_report.py --model saved_model/blood_cell_model_95_full_run1.keras --data-dir %DATA_DIR% --tta 4
python run_classification_report.py --model saved_model/blood_cell_model_95_full_run2.keras --data-dir %DATA_DIR% --tta 4
python run_classification_report.py --model saved_model/blood_cell_model_95_full_run3.keras --data-dir %DATA_DIR% --tta 4

echo Ensembling 3 runs...
python run_ensemble_report.py --models blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras --data-dir %DATA_DIR% --tta 4

echo Done. Check results\ensemble_*\classification_summary.txt for test accuracy.

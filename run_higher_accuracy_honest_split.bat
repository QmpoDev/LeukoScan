@echo off
setlocal
cd /d "%~dp0"
set PYTHON=python
if defined PYTHON_EXE set PYTHON=%PYTHON_EXE%
set DATA_DIR=data_split_full

echo === A) Existing 3 runs - ensemble with TTA=4 ===
%PYTHON% run_ensemble_report.py --models blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras --data-dir %DATA_DIR% --tta 4

echo.
echo === B) Train 3x stronger (long) ===
for %%i in (1 2 3) do %PYTHON% training_transfer_95.py --data-dir %DATA_DIR% --stronger --run-id %%i

echo.
echo === C) Ensemble stronger x3 + TTA=4 ===
%PYTHON% run_ensemble_report.py --models blood_cell_model_95_stronger_full_run1.keras blood_cell_model_95_stronger_full_run2.keras blood_cell_model_95_stronger_full_run3.keras --data-dir %DATA_DIR% --tta 4

echo.
echo === D) Optional 6-model + TTA=4 ===
%PYTHON% run_ensemble_report.py --models blood_cell_model_95_full_run1.keras blood_cell_model_95_full_run2.keras blood_cell_model_95_full_run3.keras blood_cell_model_95_stronger_full_run1.keras blood_cell_model_95_stronger_full_run2.keras blood_cell_model_95_stronger_full_run3.keras --data-dir %DATA_DIR% --tta 4

echo Done. Check results\ensemble_*\classification_summary.txt
endlocal

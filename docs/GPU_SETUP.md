# GPU Training with WSL2 (Option A)

Use WSL2 so TensorFlow can use your NVIDIA GeForce GPU. Your existing Game Ready Driver on Windows is enough; no need to install CUDA on Windows.

---

## Step 1: Install WSL2

1. Open **PowerShell as Administrator**.
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your PC if prompted.
4. After restart, **Ubuntu** (or another distro) may open to finish setup. Create a Linux username and password when asked.

To confirm WSL2 is installed:
```powershell
wsl --list --verbose
```
You should see your distro (e.g. Ubuntu) with **VERSION 2**.

---

## Step 2: Use your existing Windows driver

You already have an NVIDIA driver (e.g. Game Ready 595.71). Modern NVIDIA Windows drivers support WSL2 GPU compute. **No need to install CUDA or extra drivers on Windows.**  
If GPU doesn’t show up later, update to the latest driver from [NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx).

---

## Step 3: Open WSL and install Python + TensorFlow

1. Open **Ubuntu** (or your WSL distro) from the Start menu, or run `wsl` in PowerShell.
2. Install Python and pip, then TensorFlow and project deps:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```

3. Go to your project (Windows path under WSL):

   ```bash
   cd "/mnt/c/Users/paule/Desktop/Machine Learning/bloodcell_detection"
   ```

4. Create a venv and install requirements:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Step 4: Run training (GPU will be used if visible)

```bash
# Still in WSL, with venv active
python training.py --data-dir data_split_full
```

At the start you should see either:

- **`Using GPU: ['/physical_device:GPU:0']`** → GPU is in use; training will be much faster.
- **`No GPU found. Training on CPU.`** → See “If the GPU is not detected” below.

---

## Optional: Check GPU from Python

Inside WSL, with the same venv:

```bash
python -c "import tensorflow as tf; print('GPUs:', tf.config.list_physical_devices('GPU'))"
```

If you see `GPUs: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]`, TensorFlow sees your GPU.

---

## If the GPU is not detected ("Could not find cuda drivers" / "Error loading CUDA libraries")

The Windows driver exposes the GPU to WSL, but TensorFlow in WSL also needs the **CUDA Toolkit installed inside Ubuntu** (the runtime libraries). Do this in order:

### 1. Check if the GPU is visible in WSL

In **Ubuntu (WSL)** run:

```bash
nvidia-smi
```

- If **nvidia-smi** shows your GPU and driver version → the Windows driver is fine; go to step 2.
- If **nvidia-smi** is not found or errors → install/update the **NVIDIA driver on Windows** (latest Game Ready from [NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx)), then run `wsl --shutdown` in PowerShell and open Ubuntu again.

### 2. Install CUDA Toolkit inside WSL

In **Ubuntu (WSL)** run (adapt Ubuntu version if needed; 22.04 is common):

```bash
# Add NVIDIA package repository (Ubuntu 22.04)
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6
```

Then add the library path to your shell (add to `~/.bashrc` so it persists):

```bash
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

**Restart WSL**: in PowerShell run `wsl --shutdown`, then open Ubuntu again.

### 3. Install TensorFlow with bundled CUDA/cuDNN (fixes "cuDNN error" / "Cannot dlopen")

TensorFlow needs cuDNN. The easiest fix is to use the wheel that bundles CUDA and cuDNN:

```bash
source ~/bloodcell_venv/bin/activate
pip uninstall -y tensorflow
pip install "tensorflow[and-cuda]"
```

Then run training again:

```bash
cd "/mnt/c/Users/paule/Desktop/Machine Learning/bloodcell_detection"
python training.py --data-dir data_split_full
```

If it still says "No GPU found", check [NVIDIA CUDA on WSL User Guide](https://docs.nvidia.com/cuda/cuda-on-wsl-user-guide/index.html) for your driver/CUDA version.

### Other checks

- **Restart WSL** (PowerShell): `wsl --shutdown`, then open Ubuntu.
- **Confirm WSL2**: `wsl --list --verbose` → VERSION should be **2**.

---

## Summary: run training on GPU

| Where        | Command |
|-------------|--------|
| **Open WSL** | Start menu → Ubuntu, or `wsl` in PowerShell |
| **Go to project** | `cd "/mnt/c/Users/paule/Desktop/Machine Learning/bloodcell_detection"` |
| **Activate venv** | `source ~/bloodcell_venv/bin/activate` |
| **Train (full)** | `python training.py --data-dir data_split_full` |
| **Train (4k)**   | `python training.py --data-dir data_split_4000` |

You edit code in Windows (Cursor/VS Code) as usual; run training inside WSL so TensorFlow can use the GPU.

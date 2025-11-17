# Guide: Building a DIY GPU Server for Raspberry Pi 5 LLM Training

This guide explains how to build a dedicated GPU server that works alongside your Raspberry Pi 5. The Pi 5 acts as the manager/controller, while the GPU server handles heavy LLM training or fine-tuning. This setup is scalable, fun, and mirrors real-world edge/cloud AI workflows.

---

## 1. Overview
- **Goal:** Offload LLM training/fine-tuning from the Pi 5 to a powerful external GPU server.
- **Workflow:** Pi 5 sends jobs/data to GPU server → GPU server trains/fine-tunes model → Results/models sent back to Pi 5 for inference.

---

## 2. Hardware Shopping List
- **GPU Server:**
  - PC case (mini/micro ATX or ITX for compactness)
  - Motherboard with PCIe x16 slot
  - Powerful GPU (NVIDIA RTX 3060/3070/3090/4090, etc.)
  - CPU (mid-range, e.g., Ryzen 5, Intel i5)
  - 32GB+ RAM (16GB minimum)
  - SSD (512GB+)
  - Power supply (sized for GPU)
  - Network card (Ethernet recommended)
- **Raspberry Pi 5 (8GB)**
- **Network switch/router** (to connect both devices)
- **Cables, cooling, etc.**

---

## 3. GPU Server Setup
1. **Assemble the PC** with GPU, CPU, RAM, SSD, and network.
2. **Install Linux** (Ubuntu 22.04 LTS recommended).
3. **Install NVIDIA drivers** and CUDA toolkit:
   ```bash
   sudo apt update && sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit
   nvidia-smi  # Verify GPU is detected
   ```
4. **Install ML frameworks:**
   ```bash
   pip install torch torchvision transformers datasets
   # Add any other needed packages (e.g., bitsandbytes, accelerate)
   ```
5. **Set up SSH access:**
   - Create a user for remote access.
   - Enable SSH (`sudo systemctl enable --now ssh`).
   - Set up SSH keys for passwordless login from Pi 5.

---

## 4. Pi 5 Setup
1. **Connect Pi 5 to the same network** as the GPU server.
2. **Install SSH client and Python:**
   ```bash
   sudo apt update && sudo apt install -y openssh-client python3-pip
   ```
3. **Set up SSH keys** for secure, passwordless access to the GPU server.
4. **Install any needed Python packages** for job management (e.g., paramiko, fabric, requests).

---

## 5. Workflow: Offloading Training Jobs
### A. Manual Workflow
1. Prepare your training data on the Pi 5.
2. Use `scp` or `rsync` to copy data to the GPU server.
3. SSH into the GPU server and launch your training script (e.g., using Hugging Face Transformers).
4. When training is done, copy the resulting model files back to the Pi 5.

### B. Automated Workflow (Recommended)
- Write a Python script on the Pi 5 to:
  1. Package and send data to the GPU server.
  2. Remotely launch training via SSH.
  3. Monitor job status (poll logs, check for completion).
  4. Download the trained model when finished.
- Use libraries like `paramiko` (SSH automation) or `fabric` for scripting.

---

## 6. Example: Python Automation Script (Pi 5)
```python
import paramiko
import os

gpu_server = 'user@192.168.1.100'  # Replace with your GPU server IP
ssh_key = '/home/pi/.ssh/id_rsa'

# 1. Copy data to GPU server
os.system(f'scp -i {ssh_key} data.json {gpu_server}:~/train_data/')

# 2. Launch training remotely
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.100', username='user', key_filename=ssh_key)
stdin, stdout, stderr = ssh.exec_command('python3 train_llm.py --data ~/train_data/data.json')
print(stdout.read().decode())
ssh.close()

# 3. Download trained model
os.system(f'scp -i {ssh_key} {gpu_server}:~/output/model.gguf ./models/')
```

---

## 7. Tips & Best Practices
- Use a static IP for the GPU server for easy access.
- Automate as much as possible for repeatability.
- Monitor GPU temps and power during training.
- Use screen/tmux on the GPU server for long jobs.
- Quantize models after training for Pi 5 compatibility (e.g., GGUF format for llama.cpp).

---

## 8. Security
- Use SSH keys, not passwords.
- Limit network access to trusted devices.
- Regularly update both systems.

---

## 9. Resources
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [PyTorch](https://pytorch.org/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Paramiko](https://www.paramiko.org/)
- [Fabric](https://www.fabfile.org/)

---

## 10. Summary
With this setup, your Pi 5 can manage and delegate heavy LLM training to a dedicated GPU server, just like cloud AI—but fully under your control. This approach is scalable, fun, and ideal for personal or small-team projects.

For advanced automation or troubleshooting, see the Haven_mdev AI-project docs or ask your AI assistant!
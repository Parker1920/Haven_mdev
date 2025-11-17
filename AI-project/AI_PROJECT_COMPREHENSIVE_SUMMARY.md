# Haven_mdev AI Project: Comprehensive Guide and Integration Summary (2025+)

## Overview
This document provides a concise, information-rich summary of all major documents and workflows in the AI-project folder. It reflects the latest architecture: a single desktop with dual GPUs for LLM training, a Raspberry Pi 5 as the always-on AI hub, and the Round Table AI framework for modular, collaborative AI assistance. All references to a separate GPU workstation have been removed in favor of the dual-GPU desktop approach.

---

## 1. System Architecture & Vision
- **Raspberry Pi 5:** 24/7 backbone, running the web UI, database, Discord bot, and local LLM for fast, private, and lightweight AI tasks. Handles orchestration, automation, and user interaction.
- **Dual-GPU Desktop:** Used for training and fine-tuning LLMs on your own data/codebase. Both GPUs are managed by the same OS and Python environment, enabling efficient multi-GPU training with frameworks like PyTorch, Hugging Face Transformers, and DeepSpeed.
- **Round Table AI:** Modular set of AI assistants (Sentinel, Cartographer, Scribe, Lorekeeper, etc.), each with a focused role. The Pi 5 orchestrates which assistant and which AI resource to use for every request.
- **Cloud AI (optional):** Used only for tasks that exceed local hardware limits.

---

## 2. Key Components & Documents

### A. haven_mdev_strengths_and_vision.md
- Outlines the strengths, modularity, and future-proofing of the Haven_mdev ecosystem.
- Emphasizes local control, privacy, multi-platform collaboration, and continuous learning.
- Details the roadmap: Pi 5 as AI hub, dual-GPU desktop for LLM training, Round Table AI for orchestration, and seamless integration with Discord and mobile/PWA.

### B. master_ai_project.md
- Explains the hybrid AI model: Pi 5 for orchestration and lightweight LLM tasks, dual-GPU desktop for heavy LLM training, and cloud AI as a fallback.
- Describes the Round Table AI assistant roles and how the system decides which resource to use for each task.
- Provides workflow examples for code generation, worldbuilding, and automation.

### C. pi5_llm_coding_assistant_setup.md
- Step-by-step guide for setting up a Pi 5 as a local coding LLM assistant.
- Covers model selection, installation (llama.cpp, quantized models), and integration with the Haven_mdev workflow.
- Explains how to use the Pi 5 for code assistance, summarization, and chat.

### D. pi5_llm_codebase_adaptation_deep_dive.md
- Deep dive into making your LLM better for your codebase: fine-tuning, retrieval-augmented generation (RAG), and prompt engineering.
- Practical steps for preparing data, running fine-tuning on the dual-GPU desktop, and deploying quantized models to the Pi 5.
- RAG and prompt engineering for real-time, context-aware code and worldbuilding assistance.

### E. pi5_gpu_server_training_guide.md (now dual-GPU desktop)
- Details how to set up and use a single desktop with two GPUs for LLM training.
- Covers hardware installation, driver and CUDA setup, Python environment, and multi-GPU training commands (torchrun, accelerate, deepspeed).
- Best practices: monitor GPU usage, use mixed precision, ensure scripts support DistributedDataParallel (DDP).
- Troubleshooting: check nvidia-smi for both GPUs, resolve driver conflicts, and optimize batch size for memory.

### F. round_table_ai_chat_monitor.md
- Describes a real-time chat-style UI for visualizing AI assistant collaboration.
- Shows how each agent (Sentinel, Cartographer, etc.), the local LLM, and cloud AI interact as chat participants.
- Technical implementation: event bus/message queue backend, Web UI or Pi touchscreen frontend, live/replay modes, and filtering.

### G. RPI_CREATIVE_UPGRADES_PART1.md, RPI_CREATIVE_UPGRADES_SUMMARY.md, RPI_IMPLEMENTATION_GUIDE.md, Raspberry_Pi_5_Complete_Beginner_Guide.md, raspberry_pi_idea.md, QUICK_REFERENCE_RPI.txt, NGROK_SETUP.md
- Creative and technical ideas for Pi 5 deployment, hardware upgrades, and network setup.
- Implementation tips for always-on operation, smart home integration, and remote access.

### H. Round_table_AI_recommendations.md
- Recommendations for agent design, orchestration, and future expansion of the Round Table AI framework.

---

## 3. LLM Training on a Dual-GPU Desktop (Best Practices)
- Install both GPUs, connect power, and ensure adequate cooling.
- Use the latest NVIDIA drivers and CUDA toolkit; verify both GPUs with nvidia-smi.
- Install Python 3.9+, PyTorch, Hugging Face Transformers, accelerate, and deepspeed.
- Launch training with torchrun --nproc_per_node=2 or accelerate for multi-GPU scaling.
- Use mixed precision (fp16/bf16) for speed and memory efficiency.
- Monitor GPU temps and utilization; adjust batch size for stability.
- After training, quantize the model (e.g., GGUF for llama.cpp) and deploy to the Pi 5 for inference.

---

## 4. Troubleshooting & Tips
- If only one GPU is detected, reseat cards, check power, and reinstall drivers.
- For CUDA errors, ensure driver and CUDA versions match your PyTorch install.
- If training is slow, check PCIe slot speeds and system RAM.
- Use nvidia-smi to monitor VRAM usage and temperature; avoid thermal throttling.
- For DDP errors, verify your script supports multi-GPU and that all dependencies are up to date.

---

## 5. Summary
Haven_mdev’s AI ecosystem is now streamlined for maximum local power and privacy: the Pi 5 orchestrates, the dual-GPU desktop trains and fine-tunes, and the Round Table AI delivers modular, collaborative intelligence across all platforms. This setup is scalable, future-proof, and ready for creative expansion as your needs grow.

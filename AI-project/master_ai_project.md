# Hybrid AI Integration for Haven_mdev

## Overview
This document describes how to integrate a hybrid AI model into the Haven_mdev project, leveraging 24/7 Raspberry Pi 5 hosting, the Round Table AI, and both local and cloud-based LLMs for code generation, automation, and project management.

---

## 1. System Architecture

**Raspberry Pi 5:**
  - Acts as the 24/7 backbone of the system, hosting the web UI, database, and Discord bot.
  - Runs a local LLM (e.g., TinyLlama, Llama.cpp) for fast, private, and lightweight AI tasks.
  - Manages all project files, user data, and automations.

**Cloud AI (Claude, ChatGPT, Copilot, etc.):**
  - Used for advanced code generation, multi-file refactoring, and deep context tasks that exceed the Pi’s hardware limits.
  - Receives curated context from the Pi and returns high-quality code, documentation, or analysis.

**Round Table AI:**
  - A modular set of AI assistants (Sentinel for security, Cartographer for mapping, Scribe for data, etc.), each with a focused role.
  - Each assistant can use either the local LLM or cloud AI, depending on the complexity and privacy needs of the task.
  - The Pi orchestrates which assistant and which AI resource to use for every request.

**Example:**
  - The Cartographer assistant uses the local LLM to suggest map labels, but escalates to cloud AI for generating a new map rendering algorithm.

---

## 2. Hybrid AI Workflow

### A. Local Operations (Pi 5)
  - The Pi hosts all project files, the main database, and user interfaces (web, Discord, touchscreen).
  - Local LLM is used for:
    - Quick code suggestions (e.g., “How do I add a button in Tkinter?”)
    - Summaries and explanations (e.g., “Summarize this Python file.”)
    - Simple automations (e.g., “Auto-tag new lore entries.”)
    - Real-time event detection (e.g., “Alert if a new system is added.”)
  - Round Table AI modules default to the local LLM for privacy-sensitive or latency-critical tasks.

**Example:**
  - Scribe assistant uses the local LLM to summarize a new lore entry as soon as it’s added, without sending data to the cloud.

### B. Cloud AI Integration
  - For complex tasks (multi-file code generation, major refactors, deep analysis):
    1. The Pi gathers all relevant context (summaries, code snippets, project structure, user intent).
    2. The Pi builds a detailed prompt and sends it to the cloud AI via API or web interface.
    3. The cloud AI returns new code, documentation, or suggestions.
    4. The Pi integrates the results, runs tests, and notifies users of changes.

**Example:**
  - User requests a new map export feature. The Pi collects the map viewer code, current export logic, and user requirements, then sends it to the cloud AI for a full-featured implementation.

### C. User Interaction
  - Users interact with the system through:
    - Web dashboard: For project management, code review, and AI chat.
    - Discord bot: For quick queries, lore lookups, and admin tasks.
    - Touchscreen: For local control, map navigation, and direct access to assistants.

**Example:**
  - A user on Discord types `/feature add dark mode`, which is routed to the web dashboard for review and implementation.

---

## 3. Round Table AI in the Hybrid Model

**Assistant Roles:**
  - **Sentinel:** Monitors system health, security, and alerts. Uses local LLM for log analysis, escalates to cloud AI for anomaly detection or advanced threat modeling.
  - **Cartographer:** Handles map generation, spatial analysis, and visualization. Uses local LLM for map annotations, cloud AI for new rendering algorithms.
  - **Scribe:** Manages data entry, summarization, and documentation. Uses local LLM for summaries, cloud AI for generating comprehensive guides.
  - **Lorekeeper:** Answers lore questions, links data, and provides context. Uses local LLM for quick lookups, cloud AI for deep narrative generation.

**AI Orchestration:**
  - The Pi decides which assistant and which AI resource to use for each request, based on:
    - Task complexity (simple vs. complex)
    - Privacy (sensitive data stays local)
    - Resource needs (speed vs. depth)

**Example:**
  - Sentinel detects a suspicious login. Local LLM checks logs, but cloud AI is used to analyze patterns across multiple files and suggest security improvements.

---

## 4. Example Workflow

1. **User Requests a New Feature**
  - Through web dashboard, Discord, or touchscreen, user describes the desired feature or fix.
  - Example: “Add a button in the map viewer to export the current map as PNG.”

2. **Round Table AI Analyzes the Request**
  - The request is routed to the relevant assistant.
  - The assistant determines if the task is simple (local LLM) or complex (cloud AI).
  - Gathers all relevant context: code, files, dependencies, user permissions.
  - Example: Cartographer checks if map export is a small code change or a major feature.

3. **Local or Cloud AI Generates Code**
  - If simple: Local LLM generates code snippet (e.g., Python function for export).
  - If complex: Pi collects files, builds prompt, sends to cloud AI, receives new/updated files.
  - Example: Cloud AI returns new `export_map.py` and updates to `map_viewer.py`.

4. **Pi Integrates Results, Runs Tests, and Updates Project**
  - Pi inserts new code, runs automated tests, commits changes, or deploys to live system.
  - If issues, assistant notifies user and suggests fixes.
  - Example: New export button appears, Pi tests it, assistant troubleshoots if needed.

5. **User is Notified and Can Review or Deploy Changes**
  - User receives notification (web, Discord, touchscreen) with summary and review options.
  - Can test, approve, or request tweaks.
  - Example: “Export button added. Click to test or review code.”

**Additional Scenarios:**
  - Bug fix: Assistant gathers logs, asks AI for fix, tests, and notifies user.
  - Documentation: Assistant uses AI to generate docs from code comments.
  - Multi-file refactor: Pi collects files, cloud AI refactors, Pi integrates and tests.

---

## 5. Benefits

- **24/7 Availability:** The Pi 5 is always online, ensuring users can access the system, request features, or get help at any time.
- **Privacy for Sensitive Data:** Local LLM handles private or sensitive tasks, so user data never leaves the device unless necessary.
- **Power and Flexibility via Cloud AI:** Offloading heavy tasks to the cloud enables advanced code generation, deep analysis, and multi-file operations without hardware limits.
- **Modular, Expandable AI Assistant Framework:** The Round Table AI can be expanded with new assistants or upgraded as project needs evolve.
- **Seamless Collaboration:** Users can interact via web, Discord, or touchscreen, and all changes are tracked and reviewable.
- **Automated Testing and Integration:** Every AI-generated change is tested and integrated automatically, reducing manual work and errors.

**Example:**
- A user in another timezone requests a feature at midnight; the Pi processes it, uses cloud AI if needed, and the feature is ready by morning.

---

## 6. Implementation Tips

- **Use APIs/Webhooks:** Connect the Pi to cloud AI services using secure APIs or webhooks. Example: Use OpenAI or Anthropic APIs for code generation.
- **Automate Context Extraction:** Write scripts to summarize code, extract relevant files, and build detailed prompts for the AI.
- **Log All AI Interactions:** Keep logs of every AI request and response for transparency, debugging, and auditing.
- **User Choice:** Let users select whether to use local or cloud AI for each task, especially for privacy-sensitive operations.
- **Continuous Improvement:** Regularly update local LLMs and cloud AI integrations as new models and features become available.
- **Fallbacks and Error Handling:** If cloud AI is unavailable, the system should gracefully fall back to local LLM or queue the request.

**Example:**
- The Pi detects a failed cloud AI call and automatically retries or switches to the local LLM, notifying the user of the fallback.

---

**This architecture ensures Haven_mdev is future-proof, private, and powerful, blending the best of local and cloud AI for world-building, automation, and collaborative coding.**
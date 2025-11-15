# Raspberry Pi 5 Beginner’s Guide: Setup, Usage, and Add-Ons

## Table of Contents
1. Introduction
2. What You Need
3. Preparing Your Raspberry Pi 5
4. First Boot and Setup
5. Using the Raspberry Pi OS
6. Keeping Your Pi Updated
7. Connecting to the Internet
8. Installing and Using Add-Ons (HATs and Screens)
9. Example: Using a Touchscreen Display
10. Example: Using the AI HAT+
11. Installing and Running Software
12. Remote Access (SSH & VNC)
13. Troubleshooting
14. Best Practices & Tips
15. Resources

---

## 1. Introduction
The Raspberry Pi 5 is a powerful, affordable single-board computer. It’s perfect for learning, projects, automation, and as a low-power server. With add-ons like touchscreens and AI accelerators (HATs), you can build advanced, interactive systems.

---

## 2. What You Need
- Raspberry Pi 5 board
- Official power supply (USB-C, 5V/5A)
- microSD card (32GB+ recommended, Class 10/UHS-1)
- HDMI cable and monitor (or touchscreen add-on)
- USB keyboard and mouse
- Internet connection (Ethernet or Wi-Fi)
- Optional: Case, cooling fan, HATs (AI HAT+, touchscreen, sensors)

---

## 3. Preparing Your Raspberry Pi 5

### Step 1: Download Raspberry Pi Imager
- Go to: https://www.raspberrypi.com/software/
- Download and install the Imager for your OS (Windows, Mac, Linux).

### Step 2: Flash the microSD Card
1. Insert the microSD card into your computer.
2. Open Raspberry Pi Imager.
3. Click "Choose OS" → Select "Raspberry Pi OS (32-bit)".
4. Click "Choose Storage" → Select your microSD card.
5. Click "Write" and wait for it to finish.

**Tip:** You can pre-configure Wi-Fi and SSH by clicking the gear icon before writing.

---

## 4. First Boot and Setup
1. Insert the microSD card into the Pi.
2. Connect keyboard, mouse, and monitor (or touchscreen).
3. Plug in the power supply. The Pi will boot automatically.
4. Follow the on-screen setup:
   - Set language, time zone, and password.
   - Connect to Wi-Fi (if needed).
   - Update the system when prompted.

**Example:**
- If you see a rainbow screen, it’s booting. If nothing appears, check your cables and SD card.

---

## 5. Using the Raspberry Pi OS
- The Pi boots to a desktop (like Windows/Mac).
- Use the menu (top left) to find apps, settings, and the terminal.
- The terminal is where you type commands (e.g., `sudo apt update`).

**Example:**
- Open the terminal and type:
  ```bash
  ls
  ```
  This lists files in your home directory.

---

## 6. Keeping Your Pi Updated
Open the terminal and run:
```bash
sudo apt update
sudo apt full-upgrade
```
This keeps your system secure and up to date.

---

## 7. Connecting to the Internet
- **Wired:** Plug in Ethernet.
- **Wireless:** Click the Wi-Fi icon (top right) and select your network.

**Example:**
- If Wi-Fi doesn’t show, check that your Pi 5 model supports it and that the OS is up to date.

---

## 8. Installing and Using Add-Ons (HATs and Screens)

### What is a HAT?
- HAT = Hardware Attached on Top (add-on boards that plug into the Pi’s GPIO pins).
- Examples: AI HAT+ (for AI acceleration), touchscreens, sensors.

### Attaching a HAT
1. Power off the Pi.
2. Align the HAT’s pins with the Pi’s GPIO header.
3. Press down gently until it’s firmly seated.
4. Power on the Pi.

**Example:**
- If using a case, make sure it fits the HAT.

---

## 9. Example: Using a Touchscreen Display
1. Power off the Pi.
2. Connect the display’s ribbon cable to the Pi’s DSI port.
3. Connect power wires (if needed) to the Pi’s GPIO pins.
4. Power on the Pi. The display should light up.
5. If the display is blank, check connections and consult the display’s manual.

**Tip:** Adjust display settings in the Pi’s configuration menu if needed.

---

## 10. Example: Using the AI HAT+
1. Power off the Pi.
2. Attach the AI HAT+ to the GPIO header.
3. Power on the Pi.
4. Open the terminal.
5. Install the HAT+ software (follow the manufacturer’s instructions, usually a script or package).
   - Example:
     ```bash
     wget https://example.com/aihat-setup.sh
     chmod +x aihat-setup.sh
     ./aihat-setup.sh
     ```
6. Test the HAT+ with example code (often provided by the manufacturer).
   - Example:
     ```bash
     python3 test_aihat.py
     ```

**Tip:** Always use official instructions for your specific HAT model.

---

## 11. Installing and Running Software
- To install new programs:
  ```bash
  sudo apt install <package-name>
  ```
- For Python projects:
  ```bash
  python3 <script.py>
  ```

**Example:**
- To install Git:
  ```bash
  sudo apt install git
  ```

---

## 12. Remote Access (SSH & VNC)
- Enable SSH or VNC in the “Raspberry Pi Configuration” tool under “Interfaces.”
- Use SSH to control your Pi from another computer:
  ```bash
  ssh pi@<your-pi-ip-address>
  ```
- Use VNC for remote desktop access.

**Example:**
- Find your Pi’s IP address with:
  ```bash
  hostname -I
  ```

---

## 13. Troubleshooting
- **No boot:** Check power, SD card, and connections.
- **No display:** Check HDMI or DSI connections, try another monitor.
- **HAT not detected:** Check alignment, install drivers, consult the HAT’s manual.
- **Wi-Fi issues:** Reboot, check settings, update OS.

---

## 14. Best Practices & Tips
- Always shut down the Pi safely (use the menu or `sudo shutdown now`).
- Use a case and cooling for best performance.
- Back up your microSD card regularly.
- Use official power supplies and accessories.

---

## 15. Resources
- [Official Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)
- [Beginner Projects](https://projects.raspberrypi.org/en/)
- HAT manufacturer’s website for drivers and guides

---

**You’re ready to get started!**
If you want a printable PDF or a more advanced guide (e.g., setting up the AI HAT+ for Haven_mdev), just ask!
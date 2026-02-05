# 📸 &nbsp; Telegram Security Bot
**Motion-activated surveillance videos via Telegram**

> [!CAUTION]
> **Project Status (Historical Archive)**
> This project was developed in 2022 during my undergraduate studies and has not been actively maintained. 
> 
> **Note on Quality & Compatibility:**
> - The code structure and patterns reflect my early learning phase and do not meet my current professional standards.
> - Dependencies (Telegram Bot API, Raspberry Pi OS, etc.) may have changed since the last update. Expect to perform some manual troubleshooting to get it running on modern systems.
> - I am planning to return to this project soon for a proper rework.

---

- [🚀 Introduction](#-introduction)
- [🧳 Features](#-features)
- [📁 Installation](#-installation)
  - [Raspberry Pi Setup](#raspberry-pi-setup)
  - [Clone Project](#clone-project)
  - [Telegram Bot Creation](#create-your-telegram-bot)
  - [Setup Options](#what-are-you-up-to)
- [🛠 Hardware Setup](#-hardware-setup)
  - [Required Parts](#required-parts)
  - [Wiring](#wiring)
- [🌟 Usage](#-usage)
  - [Commands](#commands)
  - [Roles](#roles)

---

# 🚀 &nbsp; Introduction

This Telegram security bot is designed to run on a **Raspberry Pi Zero W** using a **PiCamera** and an **RCWL-0516 radar motion sensor**.

When motion is detected, the bot:
1. Notifies authorized users via text message.
2. Starts video recording.
3. Stops the recording once motion ceases.
4. Converts the video and sends it directly to the Telegram chat.

To ensure privacy, the bot includes a built-in user administration system to manage who can receive alerts and view footage.

# 🧳 &nbsp; Features

- **Remote Surveillance:** Receive security footage anywhere in the world via Telegram.
- **Access Control:** Create activation tokens to grant specific roles to other users.
- **User Management:** View, ban, or clear users directly through the bot.
- **Privacy Toggle:** Pause and resume surveillance at any time.

# 📁 &nbsp; Installation

### Raspberry Pi setup
Ensure you are using a fresh or updated Raspberry Pi OS. Use `raspi-config` to:
- **Enable the Camera** interface.
- **Enable SSH** (optional, for remote access).

### Clone Project
```bash
git clone https://github.com/ningelschlingel/telegram-security-bot.git
cd telegram-security-bot
```

### Create your Telegram-Bot
1. Create a bot via [@BotFather](https://t.me/botfather) and get your **API Token**.
2. Open `config.py` and insert your token.
3. Define a self-selected `OWNER_ACTIVATION_TOKEN` in `config.py`. You will use this to register yourself as the owner once the bot is live.

### What are you up to?
Choose your installation path. The **Script Setup** is faster, while the **Manual Setup** offers more control.

---

### Script setup
```bash
sudo ./telegram-security-bot/install.sh
```
<details>
<summary>What does this script do?</summary>
<br>

- Sets up a Python virtual environment (`venv`).
- Installs all Python dependencies.
- Installs `MP4Box` (for .h264 to .mp4 conversion).
- Configures the `.service` file with your absolute paths.
- Enables the `systemd` service to ensure the bot starts automatically on boot.
</details>

**Check service status:**
```bash
systemctl status app.service
```

---

### Manual setup
1. **Navigate into the directory:**
   ```bash
   cd telegram-security-bot
   ```
2. **Setup Virtual Environment (Optional):**
   ```bash
   python3 -m pip install virtualenv
   python3 -m virtualenv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   python3 -m pip install -r requirements.txt
   sudo apt-get install gpac # For MP4Box
   ```
4. **Start the application:**
   ```bash
   python3 app.py
   ```

# 🛠 &nbsp; Hardware setup

### Required Parts:
- Raspberry Pi Zero W
- Raspberry Pi (Zero) Camera + Ribbon Cable
- RCWL-0516 Radar Sensor

### General Tips
- **Power:** While the Pi Zero can run on battery, a dedicated power supply is recommended as video recording significantly increases power draw.
- **Interference:** The RCWL-0516 sensor can "misfire" if pressed too tightly against the Pi. Keeping a small physical gap between the sensor and the board usually solves this.

### Wiring



| RCWL-0516 Pin | Raspberry Pi Zero W Pin | Function |
| :--- | :--- | :--- |
| **VIN** | PIN 2 (5V) | Power |
| **GND** | PIN 6 (Ground) | Ground |
| **OUT** | PIN 7 (GPIO 4) | Data Signal |
| **3V3** | Not Connected | - |
| **CDS** | Not Connected | - |

*If you use a different GPIO pin, remember to update `config.py`.*

# 🌟 &nbsp; Usage

Once the bot is running, message it on Telegram and register as the owner using your token.

### Commands
Format: `/command <PARAMETER> *REQUIRED_ROLE`

| Command | Parameter | Role | Description |
| :--- | :--- | :--- | :--- |
| `/activate` | `<TOKEN>` | Open | Register your account with a token. |
| `/leave` | - | Sub+ | Leave the notification service (Owner cannot leave). |
| `/users` | - | Mod | Show all registered users. |
| `/banned` | - | Mod | Show all banned users. |
| `/token` | `<ROLE>` | Admin | Generate a new activation token for a specific role. |
| `/cleartokens`| - | Admin | Invalidate all currently pending tokens. |
| `/pause` | - | Admin | Pause motion-activated surveillance. |
| `/unpause` | - | Admin | Resume motion-activated surveillance. |
| `/ban` | - | Admin | Interactively select a user to ban. |
| `/unban` | - | Admin | Interactively select a user to unban. |
| `/clear` | - | Owner | Wipe all users and tokens from the database. |

### Roles

| Level | Role Name | Label | Permissions |
| :--- | :--- | :--- | :--- |
| **4** | `OWNER_ROLE` | Owner | Full control, video alerts, manages all users/tokens. |
| **3** | `ADMIN_ROLE` | Admin | Video alerts, creates lower-level tokens, manages users. |
| **2** | `MOD_ROLE` | Mod | Text alerts, views user lists. |
| **1** | `SUB_ROLE` | Subscriber | Text alerts only. |
| **0** | `OPEN_ROLE` | - | Can only use the `/activate` command. |
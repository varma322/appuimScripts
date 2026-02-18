# Flipkart App Stock Bot 🛒📱

A robust, high-performance Appium bot that monitors product stock and prices on the Flipkart Android app. It supports multiple delivery addresses, handles UI popups, and sends real-time Telegram alerts for restocks and price drops.

## 🚀 Features

- **Real-time Stock Monitoring**: Checks "In Stock", "Out of Stock", and "Not Deliverable" states.
- **Price Tracking**: Detects price drops below your target.
- **Multi-Address Support**: Automatically switches between configured saved addresses (e.g., Home, Office) to check deliverability.
- **Smart Automation**: 
  - Uses smart polling waits (fast reactions, no hardcoded sleeps).
  - Auto-closes popups.
  - Handles "Notify Me", "Sold Out", and ambiguous UI states.
- **Robustness**:
  - **Atomic State Saving**: Prevents data corruption if the bot crashes.
  - **Watchdog Process**: Detects crashes AND hangs (stale heartbeat), auto-restarting the bot if needed.
  - **Log Rotation & Cleanup**: Auto-rotates logs and cleans up old debug screenshots.
- **Telegram Alerts**: Instant notifications with screenshots for unknown error states.

## 🛠️ Prerequisites

- **Python 3.10+**
- **Appium Server** (running locally or remote)
- **Android Device/Emulator**
  - USB Debugging enabled.
  - Flipkart app installed and logged in.
  - Desired delivery addresses already saved in the Flipkart app.
- **ADB** (Android Debug Bridge) installed and in System PATH.

## 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/varma322/appuimScripts.git
   cd appuimScripts/flipkart-app-stock-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Environment Variables (`.env`)
Create a `.env` file in the root directory:

```ini
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
APPIUM_SERVER="http://127.0.0.1:4723"
REMINDER_SECONDS=2700  # How often to remind if still in stock (seconds)
ADDRESSES=Home,Office  # Comma-separated names of addresses saved in Flipkart app
```

### 2. Products List (`config/products.json`)
Define the items you want to track:

```json
[
    {
        "name": "Instax Mini Film",
        "url": "https://www.flipkart.com/sample-product-link...",
        "target_price": 1400
    },
    {
        "name": "Nikon Camera Bag",
        "url": "https://www.flipkart.com/sample-product-link...",
        "target_price": 1000
    }
]
```

## ▶️ Usage

### 1. Start Appium Server
Ensure your Android device is connected (`adb devices` should show it).
```bash
appium
```

### 2. Run the Bot
To run the bot directly:
```bash
python main.py
```

### 3. Run with Watchdog (Recommended)
For 24/7 monitoring, use the watchdog. It will restart the bot if it crashes or hangs.
```bash
python watchdog.py
```

## 📂 Project Structure

```
flipkart-app-stock-bot/
├── bot/
│   ├── appium_driver.py       # Appium session management
│   ├── flipkart_app_checker.py # Core logic (navigation, extraction)
│   ├── state_store.py         # JSON state management (atomic)
│   ├── telegram_notifier.py   # Telegram integration
│   └── ...
├── config/
│   └── products.json          # Target products
├── logs/                      # Rotated log files
├── screenshots/               # Debug screenshots (auto-cleaned < 3 days)
├── utils/
│   ├── logger.py              # Logging setup
│   └── cleanup.py             # Maintenance scripts
├── main.py                    # Entry point
├── watchdog.py                # Process monitor
└── requirements.txt
```

## ⚠️ Disclaimer

This tool is for educational purposes only. Automated interaction with apps may violate their Terms of Service. Use responsibly.

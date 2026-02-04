# 🎛️ Ubuntu System Dashboard

A customizable dashboard with remote PC control, task management, calendar, and weather.

## 🚀 Setup Instructions

### 1. Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project → Project Settings → Service Accounts
3. Click "Generate new private key"
4. Save the JSON file as `firebase-credentials.json` in the same folder as `system_controller.py`

### 2. Install System Controller

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install playerctl pulseaudio-utils

# Run the controller
python3 system_controller.py
```

### 3. Usage

- **Admin Panel**: Manage tasks, customize dashboard, send PC commands
- **Dashboard (index)**: View clock, weather, tasks, calendar, and send PC commands

## 🎮 Available Commands

| Command | Action |
|---------|--------|
| `play` / `pause` | Toggle media playback |
| `next` / `previous` | Skip tracks |
| `volume_up` / `volume_down` | Adjust volume |
| `mute` | Toggle mute |
| `spotify` | Open Spotify |
| `terminal` | Open Terminal |
| `browser` | Open Browser |
| `lock` | Lock screen |
| `custom` | Run any shell command |

## 🌐 Access Your Dashboard

The dashboard is deployed at: **https://7muezugzsfzwe.ok.kimi.link**

Open this on any device (phone, tablet, another PC) to control your Ubuntu PC remotely!

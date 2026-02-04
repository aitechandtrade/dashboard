#!/usr/bin/env python3
"""
Ubuntu System Media Controller
Listens to Firebase commands and controls system media/shortcuts
"""

import subprocess
import json
import os
import signal
import sys
from datetime import datetime, timedelta

# Try to import firebase, install if not present
try:
    import firebase_admin
    from firebase_admin import credentials, db
except ImportError:
    print("Installing firebase-admin...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin", "-q"])
    import firebase_admin
    from firebase_admin import credentials, db

# ============== CONFIGURATION ==============
# Download this from Firebase Console > Project Settings > Service Accounts > Generate Private Key
# Place the JSON file in the same directory as this script
FIREBASE_CREDENTIALS_FILE = "firebase-credentials.json"

# Your Firebase database URL
DATABASE_URL = "https://mydashboard-13727-default-rtdb.firebaseio.com"

# Command cooldown (seconds) - prevents duplicate commands
COMMAND_COOLDOWN = 2
# ===========================================

class SystemController:
    def __init__(self):
        self.last_command_time = datetime.now() - timedelta(seconds=10)
        self.running = True
        self.setup_firebase()
        self.setup_signal_handlers()

    def setup_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not os.path.exists(FIREBASE_CREDENTIALS_FILE):
                print(f"❌ Error: {FIREBASE_CREDENTIALS_FILE} not found!")
                print("📥 Download it from Firebase Console > Project Settings > Service Accounts")
                sys.exit(1)

            cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred, {
                'databaseURL': DATABASE_URL
            })
            print("✅ Connected to Firebase!")
        except Exception as e:
            print(f"❌ Firebase Error: {e}")
            sys.exit(1)

    def setup_signal_handlers(self):
        """Handle Ctrl+C gracefully"""
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        """Clean shutdown"""
        print("\n👋 Shutting down...")
        self.running = False
        sys.exit(0)

    def is_command_fresh(self, timestamp):
        """Check if command is recent enough to execute"""
        if not timestamp:
            return False
        cmd_time = datetime.fromtimestamp(timestamp / 1000)
        return (datetime.now() - cmd_time).total_seconds() < COMMAND_COOLDOWN

    # ============== MEDIA CONTROLS ==============
    def play_pause(self):
        """Toggle play/pause for active media"""
        subprocess.run(["playerctl", "play-pause"], capture_output=True)
        print("⏯️  Play/Pause")

    def next_track(self):
        """Next track"""
        subprocess.run(["playerctl", "next"], capture_output=True)
        print("⏭️  Next Track")

    def previous_track(self):
        """Previous track"""
        subprocess.run(["playerctl", "previous"], capture_output=True)
        print("⏮️  Previous Track")

    def volume_up(self):
        """Increase system volume"""
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"], capture_output=True)
        print("🔊 Volume Up")

    def volume_down(self):
        """Decrease system volume"""
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"], capture_output=True)
        print("🔉 Volume Down")

    def mute(self):
        """Toggle mute"""
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], capture_output=True)
        print("🔇 Mute Toggle")

    # ============== SYSTEM SHORTCUTS ==============
    def lock_screen(self):
        """Lock the screen"""
        subprocess.run(["gnome-screensaver-command", "-l"], capture_output=True)
        subprocess.run(["loginctl", "lock-session"], capture_output=True)
        print("🔒 Screen Locked")

    def screenshot(self):
        """Take screenshot"""
        subprocess.run(["gnome-screenshot", "-i"], capture_output=True)
        print("📸 Screenshot")

    def open_browser(self):
        """Open default browser"""
        subprocess.run(["xdg-open", "https://google.com"], capture_output=True)
        print("🌐 Browser Opened")

    def open_spotify(self):
        """Open Spotify"""
        subprocess.run(["spotify"], capture_output=True)
        print("🎵 Spotify Opened")

    def open_terminal(self):
        """Open terminal"""
        subprocess.run(["gnome-terminal"], capture_output=True)
        print("💻 Terminal Opened")

    # ============== CUSTOM COMMANDS ==============
    def run_custom(self, command):
        """Run a custom shell command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            print(f"⚡ Custom: {command}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Command failed: {e}")

    # ============== MAIN LOOP ==============
    def process_command(self, data):
        """Process incoming Firebase command"""
        if not data:
            return

        action = data.get('action')
        timestamp = data.get('timestamp')

        # Skip old commands
        if not self.is_command_fresh(timestamp):
            return

        # Prevent duplicate rapid commands
        now = datetime.now()
        if (now - self.last_command_time).total_seconds() < 0.5:
            return
        self.last_command_time = now

        # Route to appropriate handler
        handlers = {
            'play': self.play_pause,
            'pause': self.play_pause,
            'next': self.next_track,
            'previous': self.previous_track,
            'volume_up': self.volume_up,
            'volume_down': self.volume_down,
            'mute': self.mute,
            'lock': self.lock_screen,
            'screenshot': self.screenshot,
            'browser': self.open_browser,
            'spotify': self.open_spotify,
            'terminal': self.open_terminal,
        }

        if action in handlers:
            handlers[action]()
        elif action == 'custom' and 'command' in data:
            self.run_custom(data['command'])
        else:
            print(f"❓ Unknown action: {action}")

    def start(self):
        """Start listening for commands"""
        print("🚀 System Controller Started!")
        print("📱 Ready to receive commands from your dashboard...")
        print("   - Use Play/Pause buttons for media control")
        print("   - Add volume controls to your dashboard for volume")
        print("")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        # Listen to Firebase
        media_ref = db.reference('media')

        def listener(event):
            if event.data:
                self.process_command(event.data)

        media_ref.listen(listener)

        # Keep running
        while self.running:
            import time
            time.sleep(1)


def install_dependencies():
    """Check and install required system packages"""
    print("🔧 Checking dependencies...")

    # Check for playerctl (media control)
    result = subprocess.run(["which", "playerctl"], capture_output=True)
    if result.returncode != 0:
        print("📦 Installing playerctl...")
        subprocess.run(["sudo", "apt-get", "update", "-qq"], capture_output=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "-qq", "playerctl"], capture_output=True)
        print("✅ playerctl installed")
    else:
        print("✅ playerctl already installed")

    # Check for pactl (volume control)
    result = subprocess.run(["which", "pactl"], capture_output=True)
    if result.returncode != 0:
        print("⚠️  pactl not found. Install pulseaudio-utils for volume control.")


if __name__ == "__main__":
    print("=" * 50)
    print("   🎛️  Ubuntu System Controller")
    print("=" * 50)
    print("")

    # Install dependencies
    install_dependencies()
    print("")

    # Start controller
    controller = SystemController()
    controller.start()

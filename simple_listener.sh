#!/bin/bash
# Simple bash listener for Firebase (requires curl and jq)
# This is a lightweight alternative to the Python controller

DATABASE_URL="https://mydashboard-13727-default-rtdb.firebaseio.com"
LAST_TIMESTAMP=0

echo "🎛️  Simple System Listener"
echo "=========================="
echo "Checking for playerctl..."

if ! command -v playerctl &> /dev/null; then
    echo "Installing playerctl..."
    sudo apt-get update -qq && sudo apt-get install -y -qq playerctl
fi

echo "✅ Ready! Listening for commands..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Fetch latest command from Firebase
    RESPONSE=$(curl -s "${DATABASE_URL}/media.json" 2>/dev/null)
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        ACTION=$(echo "$RESPONSE" | jq -r '.action // empty')
        TIMESTAMP=$(echo "$RESPONSE" | jq -r '.timestamp // 0')
        
        # Check if command is new (within last 3 seconds)
        CURRENT_TIME=$(date +%s%3N)
        TIME_DIFF=$((CURRENT_TIME - TIMESTAMP))
        
        if [ "$TIME_DIFF" -lt 3000 ] && [ "$TIMESTAMP" -ne "$LAST_TIMESTAMP" ]; then
            LAST_TIMESTAMP=$TIMESTAMP
            
            case "$ACTION" in
                "play"|"pause")
                    playerctl play-pause
                    echo "⏯️  Play/Pause"
                    ;;
                "next")
                    playerctl next
                    echo "⏭️  Next Track"
                    ;;
                "previous")
                    playerctl previous
                    echo "⏮️  Previous Track"
                    ;;
                "volume_up")
                    pactl set-sink-volume @DEFAULT_SINK@ +5%
                    echo "🔊 Volume Up"
                    ;;
                "volume_down")
                    pactl set-sink-volume @DEFAULT_SINK@ -5%
                    echo "🔉 Volume Down"
                    ;;
                "mute")
                    pactl set-sink-mute @DEFAULT_SINK@ toggle
                    echo "🔇 Mute Toggle"
                    ;;
                "spotify")
                    spotify &
                    echo "🎵 Spotify"
                    ;;
                "terminal")
                    gnome-terminal &
                    echo "💻 Terminal"
                    ;;
                "browser")
                    xdg-open https://google.com &
                    echo "🌐 Browser"
                    ;;
                "lock")
                    loginctl lock-session
                    echo "🔒 Screen Locked"
                    ;;
                *)
                    echo "❓ Unknown: $ACTION"
                    ;;
            esac
        fi
    fi
    
    # Poll every 500ms
    sleep 0.5
done

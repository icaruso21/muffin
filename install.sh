#!/bin/bash

# NYC MTA Subway Display Installation Script for Raspberry Pi
# This script sets up the MTA display application to run on boot

set -e

echo "🚇 Installing NYC MTA Subway Display..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create application directory
APP_DIR="/home/pi/mta-display"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p "$APP_DIR"

# Get current user (works on both Pi and other systems)
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)
echo "👤 Using user: $CURRENT_USER:$CURRENT_GROUP"
sudo chown $CURRENT_USER:$CURRENT_GROUP "$APP_DIR"

# Copy application files
echo "📋 Copying application files..."
sudo cp mta_display.py "$APP_DIR/"
sudo cp requirements.txt "$APP_DIR/"
sudo cp config.env.example "$APP_DIR/"
sudo chown $CURRENT_USER:$CURRENT_GROUP "$APP_DIR"/*

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-pygame python3-requests python3-geopy
else
    echo "   Skipping apt-get (not on Linux). Please install dependencies manually:"
    echo "   pip3 install -r requirements.txt"
fi

# Install Python packages
pip3 install -r requirements.txt

# Set up environment configuration
echo "⚙️  Setting up configuration..."
if [ ! -f "$APP_DIR/config.env" ]; then
    cp "$APP_DIR/config.env.example" "$APP_DIR/config.env"
    echo "📝 Created config.env file. Please edit it with your MTA API key and settings."
    echo "   Location: $APP_DIR/config.env"
fi

# Install systemd service (only on Linux systems)
echo "🔧 Installing systemd service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Create dynamic service file with current user
    cat > /tmp/mta-display.service << EOF
[Unit]
Description=NYC MTA Subway Display
After=network.target graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_GROUP
WorkingDirectory=$APP_DIR
Environment=DISPLAY=:0
Environment=PYTHONPATH=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/mta_display.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical-session.target
EOF
    
    sudo cp /tmp/mta-display.service /etc/systemd/system/mta-display.service
    sudo systemctl daemon-reload
    sudo systemctl enable mta-display.service
    rm /tmp/mta-display.service
else
    echo "   Skipping systemd service (not on Linux)"
    echo "   To run on macOS, use: python3 mta_display.py"
fi

# Set up display permissions (only on Linux systems)
echo "🖥️  Setting up display permissions..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo usermod -a -G video $CURRENT_USER
else
    echo "   Skipping display permissions setup (not on Linux)"
fi

# Create startup script
echo "🚀 Creating startup script..."
cat > "$APP_DIR/start.sh" << 'EOF'
#!/bin/bash
# Wait for X server to be ready
sleep 10
export DISPLAY=:0
cd /home/pi/mta-display
python3 mta_display.py
EOF

chmod +x "$APP_DIR/start.sh"

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit $APP_DIR/config.env with your MTA API key"
echo "2. Get your MTA API key from: https://api.mta.info/"
echo "3. Configure your location and preferred station"
echo "4. Start the service: sudo systemctl start mta-display"
echo "5. Check status: sudo systemctl status mta-display"
echo ""
echo "🎮 Controls:"
echo "   - ESC or close window to exit"
echo "   - F11 to toggle fullscreen"
echo ""
echo "📊 Logs:"
echo "   - View logs: journalctl -u mta-display -f"
echo "   - Stop service: sudo systemctl stop mta-display"
echo ""
echo "🔄 The application will start automatically on boot!"

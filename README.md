# NYC MTA Subway Display for Raspberry Pi 🚇

A Python application that displays real-time NYC MTA subway arrival times in the authentic style of official subway station displays. Perfect for your Raspberry Pi to create your own subway information display!

## Features

- 🚇 **Authentic MTA Design**: Replicates the look and feel of official NYC subway displays
- 🎨 **Route Colors**: All subway lines with their official MTA colors
- 📍 **Location-Based**: Shows nearby stations based on your location
- 🔄 **Real-Time Updates**: Fetches live data from MTA's GTFS API
- 🖥️ **Fullscreen Display**: Perfect for dedicated display setups
- 🚀 **Auto-Start**: Runs automatically on boot via systemd
- ⚙️ **Configurable**: Easy configuration via environment variables

## Screenshots

The display shows:
- Station name at the top
- Current time
- Upcoming trains with route circles, destinations, and arrival times
- Last updated timestamp
- Authentic MTA color scheme and typography

## Quick Start

### 1. MTA Data Access

✅ **Free Public Feeds**: MTA real-time data is available without an API key!
- Visit [MTA API Documentation](https://api.mta.info/#/subwayRealTimeFeeds) for details
- All GTFS Real-Time feeds are publicly accessible
- Optional: Get an API key for higher rate limits

### 2. Install on Raspberry Pi

```bash
# Clone or download this repository
git clone <your-repo-url>
cd muffin

# Run the installation script
./install.sh
```

### 3. Test MTA API Connection

Test the MTA API connection:
```bash
# Test your API connection
python test_api.py
```

This will verify that the MTA feeds are accessible.

### 4. Configure

Edit the configuration file:
```bash
nano /home/pi/mta-display/config.env
```

Set your preferences:
```env
# MTA_API_KEY=optional_api_key_here  # Optional for higher rate limits
LATITUDE=40.6843
LONGITUDE=-73.9779
STATION_ID=<ENTERHERE>
STATION_NAME=Atlantic Av-Barclays Ctr
REFRESH_INTERVAL=30
FULLSCREEN=true
```

### 4. Start the Service

```bash
# Start the display
sudo systemctl start mta-display

# Check if it's running
sudo systemctl status mta-display

# View logs
journalctl -u mta-display -f
```

## Manual Installation

If you prefer to install manually:

### Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pygame python3-requests python3-geopy
pip3 install -r requirements.txt
```

### Configuration

1. Copy `config.env.example` to `config.env`
2. Edit with your settings
3. Set up the systemd service:
   ```bash
   sudo cp mta-display.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable mta-display.service
   ```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `MTA_API_KEY` | Your MTA API key (optional) | - |
| `LATITUDE` | Your latitude for nearby stations | 40.7589 |
| `LONGITUDE` | Your longitude for nearby stations | -73.9851 |
| `STATION_ID` | Specific station ID to monitor | - |
| `STATION_NAME` | Display name for the station | Times Sq-42 St |
| `REFRESH_INTERVAL` | Seconds between API updates | 30 |
| `FULLSCREEN` | Run in fullscreen mode | true |

## Controls

- **ESC** or **Close Window**: Exit the application
- **F11**: Toggle fullscreen mode

## Service Management

```bash
# Start the service
sudo systemctl start mta-display

# Stop the service
sudo systemctl stop mta-display

# Restart the service
sudo systemctl restart mta-display

# Check status
sudo systemctl status mta-display

# View logs
journalctl -u mta-display -f

# Disable auto-start
sudo systemctl disable mta-display
```

## Troubleshooting

### Display Issues
- Ensure your Pi is connected to a display
- Check that the `pi` user is in the `video` group: `groups pi`
- Try running manually: `python3 mta_display.py`

### API Issues
- Check your internet connection
- View logs for specific error messages: `journalctl -u mta-display -f`
- Note: API key is no longer required for MTA feeds

### Service Won't Start
- Check the service status: `sudo systemctl status mta-display`
- Verify the configuration file exists and is readable
- Ensure all dependencies are installed

## Development

### Running in Development Mode

```bash
# Set environment variables (API key optional)
export FULLSCREEN=false

# Run directly
python3 mta_display.py
```

### Project Structure

```
muffin/
├── mta_display.py          # Main application
├── requirements.txt        # Python dependencies
├── config.env.example     # Configuration template
├── mta-display.service    # Systemd service file
├── install.sh             # Installation script
└── README.md              # This file
```

## API Information

This application uses the MTA's GTFS Real-Time API:
- **Documentation**: [MTA Developer Resources](https://api.mta.info/)
- **Feed Types**: All subway lines (1,2,3,4,5,6,A,C,E,B,D,F,M,G,J,Z,L,N,Q,R,W,S)
- **Update Frequency**: Every 30 seconds (configurable)

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NYC MTA for providing the real-time data API
- The open-source community for the Python libraries used
- Raspberry Pi Foundation for making this hardware possible

---

**Note**: This is an unofficial application and is not affiliated with the MTA. Use responsibly and in accordance with the MTA's API terms of service.
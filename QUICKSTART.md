# Quick Start Guide 🚀

Get your NYC MTA subway display running in 5 minutes!

## Step 1: Get Your API Key (2 minutes)

1. **Visit**: [MTA Developer Resources](https://api.mta.info/)
2. **Sign up** for a free account
3. **Request access** to GTFS Real-Time feeds
4. **Copy your API key** (you'll need it in step 3)

## Step 2: Test Locally (1 minute)

```bash
# Test the display with mock data
python3 test_display.py
```

This shows you what the display will look like with sample subway data.

## Step 3: Set Up Configuration (1 minute)

```bash
# Run the setup helper
python3 setup_api.py
```

This will:
- Open the MTA developer page
- Test your API key
- Create your `config.env` file

## Step 4: Install on Raspberry Pi (1 minute)

```bash
# Copy files to your Pi (or clone the repo)
scp -r . pi@your-pi-ip:/home/pi/mta-display/

# SSH into your Pi
ssh pi@your-pi-ip

# Run the installer
cd mta-display
./install.sh
```

## Step 5: Start the Display

```bash
# Start the service
sudo systemctl start mta-display

# Check it's running
sudo systemctl status mta-display
```

## That's It! 🎉

Your Pi will now show real-time NYC subway times in authentic MTA style!

### Quick Commands

```bash
# View logs
journalctl -u mta-display -f

# Stop the display
sudo systemctl stop mta-display

# Restart the display
sudo systemctl restart mta-display

# Disable auto-start
sudo systemctl disable mta-display
```

### Troubleshooting

- **No display?** Check logs: `journalctl -u mta-display -f`
- **API errors?** Verify your API key in `/home/pi/mta-display/config.env`
- **Service won't start?** Check status: `sudo systemctl status mta-display`

---

**Need help?** Check the full [README.md](README.md) for detailed instructions!

#!/usr/bin/env python3
"""
MTA API Setup Helper
This script helps you get started with the MTA API
"""

import os
import webbrowser
import requests
from urllib.parse import urljoin

def open_mta_developer_page():
    """Open the MTA developer resources page"""
    url = "https://api.mta.info/"
    print(f"🌐 Opening MTA Developer Resources: {url}")
    webbrowser.open(url)
    print("📋 Please follow these steps:")
    print("1. Sign up for an account")
    print("2. Request access to GTFS Real-Time feeds")
    print("3. Copy your API key")
    print("4. Return here and enter your API key")

def test_api_key(api_key):
    """Test if the API key works"""
    if not api_key:
        return False, "No API key provided"
    
    # Test with a simple request
    test_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsrealtime/nyct%2Fgtfs-123456"
    headers = {'x-api-key': api_key}
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, "API key is valid!"
        elif response.status_code == 401:
            return False, "Invalid API key"
        elif response.status_code == 403:
            return False, "API key doesn't have access to this feed"
        else:
            return False, f"Unexpected response: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {e}"

def setup_config():
    """Set up the configuration file"""
    config_path = "config.env"
    
    print("\n⚙️  Setting up configuration...")
    
    # Get API key
    api_key = input("Enter your MTA API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Test the API key
    print("🔍 Testing API key...")
    is_valid, message = test_api_key(api_key)
    print(f"   {message}")
    
    if not is_valid:
        print("❌ API key test failed. Please check your key and try again.")
        return
    
    # Get location preferences
    print("\n📍 Location Configuration:")
    print("   You can use GPS coordinates or a specific station")
    
    use_gps = input("Use GPS coordinates? (y/N): ").strip().lower() == 'y'
    
    if use_gps:
        try:
            lat = float(input("Enter latitude (e.g., 40.7589): "))
            lon = float(input("Enter longitude (e.g., -73.9851): "))
        except ValueError:
            print("❌ Invalid coordinates. Using default location.")
            lat, lon = 40.7589, -73.9851
    else:
        lat, lon = 40.7589, -73.9851
    
    # Get station name
    station_name = input("Enter station display name (e.g., 'Times Sq-42 St'): ").strip()
    if not station_name:
        station_name = "Times Sq-42 St"
    
    # Get other preferences
    refresh_interval = input("Refresh interval in seconds (default 30): ").strip()
    if not refresh_interval.isdigit():
        refresh_interval = "30"
    
    fullscreen = input("Run in fullscreen? (Y/n): ").strip().lower()
    if fullscreen == 'n':
        fullscreen = "false"
    else:
        fullscreen = "true"
    
    # Write config file
    config_content = f"""# MTA API Configuration
MTA_API_KEY={api_key}

# Location Configuration
LATITUDE={lat}
LONGITUDE={lon}

# Station Configuration
STATION_NAME={station_name}

# Display Configuration
REFRESH_INTERVAL={refresh_interval}
FULLSCREEN={fullscreen}
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuration saved to {config_path}")
    print("\n🚀 You're ready to go! Next steps:")
    print("1. Run the test display: python3 test_display.py")
    print("2. Or install on your Pi: ./install.sh")

def main():
    """Main setup function"""
    print("🚇 MTA API Setup Helper")
    print("=" * 40)
    
    # Check if config already exists
    if os.path.exists("config.env"):
        overwrite = input("config.env already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Open MTA developer page
    open_mta_developer_page()
    
    # Wait for user to get API key
    input("\nPress Enter when you have your API key...")
    
    # Set up configuration
    setup_config()

if __name__ == "__main__":
    main()

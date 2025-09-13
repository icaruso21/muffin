#!/usr/bin/env python3
"""
Test script to verify MTA API connection and get station information
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_mta_api():
    """Test MTA API connection and display available stations"""
    api_key = os.getenv('MTA_API_KEY')
    
    if api_key:
        print(f"🔑 Using API key: {api_key[:8]}...")
    else:
        print("ℹ️  No API key provided - using free public feeds")
    
    # Test with a simple feed request using the correct free endpoints
    test_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"  # 1234567S feed
    
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
    
    try:
        print(f"🌐 Testing connection to: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"📏 Response size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if we got protobuf data (even if content-type is wrong)
            if len(response.content) > 1000 and b'\x03' in response.content[:100]:
                print("✅ SUCCESS! MTA API is working and returning protobuf data")
                print(f"📊 Received {len(response.content)} bytes of real-time data")
                return True
            else:
                print(f"⚠️  Warning: Expected protobuf data, got: {response.headers.get('content-type')}")
                print(f"📄 Response preview: {response.content[:200]}")
                return False
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def show_station_info():
    """Show information about Atlantic Ave - Barclays Center station (default)"""
    print("\n🏛️  Atlantic Ave - Barclays Center Station Info (Default):")
    print("   Station ID: A42 (2,3,4,5 lines)")
    print("   Station ID: R30 (B,D,N,Q,R lines)")
    print("   Location: 40.6843° N, 73.9779° W")
    print("   Address: 4th Ave & Atlantic Ave, Brooklyn, NY")
    print("   This is now the default station in the configuration!")

if __name__ == "__main__":
    print("🚇 MTA API Test Script")
    print("=" * 50)
    
    success = test_mta_api()
    show_station_info()
    
    if success:
        print("\n🎉 MTA API connection is working correctly!")
        print("   You can now run: python mta_display.py")
    else:
        print("\n🔧 There seems to be an issue with the MTA API connection.")
        print("   The feeds should be free and accessible without an API key.")

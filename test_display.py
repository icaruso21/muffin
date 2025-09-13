#!/usr/bin/env python3
"""
Test script for MTA Display
Run this to test the display without needing real MTA API data
"""

import os
import sys
import pygame
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mta_display import MTADisplay

class TestMTADisplay(MTADisplay):
    """Test version of MTA Display with mock data"""
    
    def __init__(self):
        # Set up test environment variables
        # No API key needed - MTA feeds are now free!
        os.environ['LATITUDE'] = '40.7589'
        os.environ['LONGITUDE'] = '-73.9851'
        os.environ['STATION_NAME'] = 'Times Sq-42 St'
        os.environ['FULLSCREEN'] = 'false'
        os.environ['REFRESH_INTERVAL'] = '5'
        
        super().__init__()
    
    def fetch_mta_data(self):
        """Return mock MTA data for testing"""
        current_time = datetime.now()
        
        mock_arrivals = [
            {
                'route_id': '1',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=2),
                'destination': 'To South Ferry',
                'status': 'On Time'
            },
            {
                'route_id': '2',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=4),
                'destination': 'To Flatbush Av',
                'status': 'On Time'
            },
            {
                'route_id': '3',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=6),
                'destination': 'To New Lots Av',
                'status': 'On Time'
            },
            {
                'route_id': 'A',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=3),
                'destination': 'To Far Rockaway',
                'status': 'On Time'
            },
            {
                'route_id': 'C',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=5),
                'destination': 'To Euclid Av',
                'status': 'On Time'
            },
            {
                'route_id': 'E',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=7),
                'destination': 'To Jamaica Center',
                'status': 'On Time'
            },
            {
                'route_id': 'N',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=1),
                'destination': 'To Coney Island',
                'status': 'Now'
            },
            {
                'route_id': 'Q',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=8),
                'destination': 'To Coney Island',
                'status': 'On Time'
            },
            {
                'route_id': 'R',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=9),
                'destination': 'To Bay Ridge-95 St',
                'status': 'On Time'
            },
            {
                'route_id': 'W',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=11),
                'destination': 'To Astoria-Ditmars Blvd',
                'status': 'On Time'
            },
            {
                'route_id': 'L',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=13),
                'destination': 'To Canarsie-Rockaway Pkwy',
                'status': 'On Time'
            },
            {
                'route_id': 'G',
                'station_id': 'test_station',
                'arrival_time': current_time + timedelta(minutes=15),
                'destination': 'To Church Av',
                'status': 'On Time'
            }
        ]
        
        return mock_arrivals

def main():
    """Run the test display"""
    print("🧪 Starting MTA Display Test Mode...")
    print("This will show mock subway data for testing purposes.")
    print("Press ESC to exit, F11 to toggle fullscreen")
    
    try:
        app = TestMTADisplay()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Test display stopped by user")
    except Exception as e:
        print(f"❌ Test display error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

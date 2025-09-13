#!/usr/bin/env python3
"""
NYC MTA Subway Display for Raspberry Pi
Displays real-time subway arrival times in MTA-style signage
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pygame
from dotenv import load_dotenv
from geopy.distance import geodesic
import logging

try:
    from google.transit import gtfs_realtime_pb2
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False
    logging.warning("GTFS protobuf bindings not available. Install with: pip install gtfs-realtime-bindings")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MTADisplay:
    def __init__(self):
        """Initialize the MTA Display application"""
        self.api_key = os.getenv('MTA_API_KEY')  # Optional - feeds are free
        if not self.api_key:
            logger.info("No MTA API key provided - using free public feeds")
        
        self.latitude = float(os.getenv('LATITUDE', '40.6843'))
        self.longitude = float(os.getenv('LONGITUDE', '-73.9779'))
        self.station_id = os.getenv('STATION_ID', 'A42')
        self.station_name = os.getenv('STATION_NAME', 'Atlantic Av-Barclays Ctr')
        self.refresh_interval = int(os.getenv('REFRESH_INTERVAL', '30'))
        self.fullscreen = os.getenv('FULLSCREEN', 'true').lower() == 'true'
        
        # MTA API endpoints - Free public feeds (no API key required)
        self.feed_urls = {
            '1234567S': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
            'ACEH': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
            'BDFMFS': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
            'G': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
            'JZ': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
            'NQRW': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
            'L': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
            'SIR': "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si"
        }
        
        # Initialize Pygame
        pygame.init()
        self.setup_display()
        self.setup_fonts()
        
        # MTA color scheme - matching the real display
        self.colors = {
            'background': (0, 20, 60),        # Dark blue background like real MTA signs
            'text_primary': (135, 206, 250),  # Light blue text
            'text_secondary': (200, 220, 255), # Lighter blue for secondary text
            'text_white': (255, 255, 255),    # White text
            'frame': (0, 0, 0),               # Black frame
            'status_light': (0, 255, 0),      # Green status light
            # Route colors - matching MTA official colors
            'route_1': (238, 42, 36),         # Red
            'route_2': (0, 57, 166),          # Blue
            'route_3': (0, 163, 65),          # Green
            'route_4': (255, 99, 25),         # Orange
            'route_5': (163, 38, 56),         # Purple
            'route_6': (0, 118, 50),          # Dark Green
            'route_7': (255, 255, 0),         # Yellow
            'route_A': (0, 57, 166),          # Blue
            'route_B': (255, 99, 25),         # Orange (B line)
            'route_C': (0, 57, 166),          # Blue
            'route_D': (0, 57, 166),          # Blue
            'route_E': (0, 57, 166),          # Blue
            'route_F': (255, 99, 25),         # Orange (F line)
            'route_G': (108, 190, 69),        # Light Green
            'route_J': (153, 102, 51),        # Brown
            'route_L': (166, 86, 40),         # Light Brown
            'route_M': (0, 57, 166),          # Blue
            'route_N': (255, 255, 0),         # Yellow
            'route_Q': (255, 255, 0),         # Yellow
            'route_R': (255, 255, 0),         # Yellow
            'route_S': (128, 128, 128),       # Gray
            'route_W': (255, 255, 0),         # Yellow
            'route_Z': (153, 102, 51),        # Brown
        }
        
        self.running = True
        
    def setup_display(self):
        """Initialize the display window"""
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1200, 800))
        
        pygame.display.set_caption("NYC MTA Subway Times")
        self.clock = pygame.time.Clock()
        
    def setup_fonts(self):
        """Load fonts for the display"""
        try:
            # Fonts sized to match the real MTA display
            self.sequence_font = pygame.font.Font(None, 36)      # Small sequence numbers
            self.route_font = pygame.font.Font(None, 42)         # Route letters in circles
            self.destination_font = pygame.font.Font(None, 48)   # Main destination text
            self.detail_font = pygame.font.Font(None, 32)        # Secondary details
            self.time_font = pygame.font.Font(None, 40)          # Arrival times
            self.time_unit_font = pygame.font.Font(None, 24)     # "MM" for minutes
        except:
            # Fallback to default font
            self.sequence_font = pygame.font.Font(None, 36)
            self.route_font = pygame.font.Font(None, 42)
            self.destination_font = pygame.font.Font(None, 48)
            self.detail_font = pygame.font.Font(None, 32)
            self.time_font = pygame.font.Font(None, 40)
            self.time_unit_font = pygame.font.Font(None, 24)
    
    def get_route_color(self, route_id: str) -> tuple:
        """Get the color for a specific route"""
        route_key = f"route_{route_id}"
        return self.colors.get(route_key, self.colors['text_primary'])
    
    def fetch_mta_data(self) -> List[Dict]:
        """Fetch real-time data from MTA API"""
        all_arrivals = []
        
        for feed_name, url in self.feed_urls.items():
            try:
                headers = {}
                if self.api_key:
                    headers['x-api-key'] = self.api_key
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                logger.info(f"Response status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                # Parse protobuf data
                arrivals = self.parse_feed_data(response.content, feed_name)
                all_arrivals.extend(arrivals)
                
            except Exception as e:
                logger.error(f"Error fetching data from {feed_name}: {e}")
                continue
        
        return all_arrivals
    
    def parse_feed_data(self, data: bytes, feed_name: str) -> List[Dict]:
        """Parse real MTA feed data using protobuf"""
        if not PROTOBUF_AVAILABLE:
            logger.error("Protobuf not available - cannot parse MTA data")
            return []

        try:
            logger.info(f"Parsing {len(data)} bytes of data from {feed_name}")
            # Check if we got an error response instead of protobuf data
            if len(data) < 1000:  # Likely an error response
                logger.error(f"Received error response ({len(data)} bytes) from MTA API. Data: {data[:100]}")
                return []
            
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(data)
            
            logger.info(f"Feed has {len(feed.entity)} entities")
            arrivals = []
            current_time = datetime.now()
            
            # Station ID mapping for Atlantic Ave - Barclays Center
            # A42 serves: 2,3,4,5 lines
            # R30 serves: B,D,N,Q,R lines
            target_stations = {
                'A42': ['2', '3', '4', '5'],  # Lines that serve A42
                'R30': ['B', 'D', 'N', 'Q', 'R'],  # Lines that serve R30
            }
            
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip_update = entity.trip_update
                    
                    # Get route ID
                    route_id = trip_update.trip.route_id
                    
                    # Check if this trip has stops at our target station
                    for stop_update in trip_update.stop_time_update:
                        stop_id = stop_update.stop_id
                        
                        # Check if this route serves this station
                        station_served = False
                        for station_id, serving_routes in target_stations.items():
                            if station_id in stop_id and route_id in serving_routes:
                                station_served = True
                                break
                        
                        if station_served:
                            if stop_update.HasField('arrival'):
                                arrival_time = datetime.fromtimestamp(stop_update.arrival.time)
                                
                                # Only show arrivals in the next 30 minutes
                                if arrival_time > current_time and (arrival_time - current_time).total_seconds() < 1800:
                                    # Get trip details
                                    trip = trip_update.trip
                                    # Handle different field names for trip headsign
                                    headsign = getattr(trip, 'trip_headsign', None) or getattr(trip, 'headsign', None)
                                    
                                    # Note: MTA real-time feeds don't include trip_headsign
                                    # We'll use fallback destinations based on route
                                    
                                    destination = self._get_destination_name(headsign, route_id)
                                    
                                    arrivals.append({
                                        'route_id': route_id,
                                        'station_id': stop_id,
                                        'arrival_time': arrival_time,
                                        'destination': destination,
                                        'detail': self._get_route_detail(route_id),
                                        'status': 'On Time'
                                    })
            
            # Sort by arrival time and limit to 4 per feed
            arrivals.sort(key=lambda x: x['arrival_time'])
            return arrivals[:4]
            
        except Exception as e:
            logger.error(f"Error parsing protobuf data: {e}")
            return []
    
    
    def _get_destination_name(self, headsign: str, route_id: str = None) -> str:
        """Clean up destination names from MTA data"""
        if not headsign or headsign == "Unknown":
            # Provide fallback destinations based on route
            fallback_destinations = {
                '1': '242 St', '2': 'Flatbush Av', '3': 'Jamaica Center', '4': 'Woodlawn', 
                '5': '242 St', '6': 'Pelham Bay Park', '7': 'Flushing-Main St',
                'A': 'Inwood-207 St', 'C': 'Euclid Av', 'E': 'Jamaica Center',
                'B': 'Brighton Beach', 'D': 'Coney Island', 'F': 'Jamaica-179 St', 'M': 'Middle Village',
                'G': 'Church Av', 'J': 'Jamaica Center', 'Z': 'Jamaica Center', 'L': 'Canarsie-Rockaway Pkwy',
                'N': 'Coney Island', 'Q': 'Coney Island', 'R': 'Bay Ridge-95 St', 'W': 'Astoria-Ditmars Blvd',
                'S': 'Times Sq-42 St'
            }
            return fallback_destinations.get(route_id, "Unknown")
        
        # Remove common prefixes and clean up
        headsign = headsign.replace("To ", "").replace("TO ", "")
        return headsign.strip()
    
    def _get_route_detail(self, route_id: str) -> str:
        """Get route detail based on route ID"""
        details = {
            '1': '242 St', '2': 'Flatbush Av', '3': 'Jamaica Center', '4': 'Woodlawn', '5': '242 St', '6': 'Pelham Bay Park',
            'A': 'Inwood-207 St', 'C': 'Euclid Av', 'E': 'Jamaica Center',
            'B': 'Brighton Beach', 'D': 'Coney Island', 'F': 'Jamaica-179 St', 'M': 'Middle Village',
            'G': 'Church Av', 'J': 'Jamaica Center', 'Z': 'Jamaica Center', 'L': 'Canarsie-Rockaway Pkwy',
            'N': 'Coney Island', 'Q': 'Coney Island', 'R': 'Bay Ridge-95 St', 'W': 'Astoria-Ditmars Blvd',
            'S': 'Times Sq-42 St'
        }
        return details.get(route_id, 'Unknown')
    
    def filter_nearby_stations(self, arrivals: List[Dict]) -> List[Dict]:
        """Filter arrivals to show only nearby stations"""
        # For now, return all arrivals since we're using realistic mock data
        # In a real implementation, you'd filter by distance from your location
        return arrivals[:4]  # Show max 4 arrivals like real MTA displays
    
    def format_time_remaining(self, arrival_time: datetime) -> str:
        """Format time remaining until arrival"""
        now = datetime.now()
        delta = arrival_time - now
        
        if delta.total_seconds() < 0:
            return "Now"
        elif delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s"
        else:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
    
    def draw_route_circle(self, surface, x: int, y: int, route_id: str, radius: int = 30):
        """Draw a route circle in MTA style"""
        color = self.get_route_color(route_id)
        pygame.draw.circle(surface, color, (x, y), radius)
        
        # Draw route text in white
        text_surface = self.route_font.render(route_id, True, self.colors['text_white'])
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    
    def draw_arrival(self, surface, x: int, y: int, arrival: Dict, sequence_num: int):
        """Draw a single arrival entry matching the real MTA display layout"""
        route_id = arrival['route_id']
        destination = arrival['destination']
        time_remaining = self.format_time_remaining(arrival['arrival_time'])
        
        # Draw very subtle background rectangle for each entry (with more vertical padding)
        entry_rect = pygame.Rect(x + 10, y + 5, self.screen.get_width() - 80, 80)  # Increased height to 80
        pygame.draw.rect(surface, (5, 15, 35), entry_rect)  # Very subtle background
        # Remove the border for cleaner look
        
        # Draw sequence number (left side)
        seq_surface = self.sequence_font.render(str(sequence_num), True, self.colors['text_primary'])
        surface.blit(seq_surface, (x + 20, y + 20))  # Shifted down by 5 pixels
        
        # Draw route circle (centered within the taller entry box)
        # New entry box is from y+5 to y+85, so center is at y+45
        self.draw_route_circle(surface, x + 80, y + 45, route_id, radius=25)
        
        # Draw main destination (larger, bold text)
        dest_surface = self.destination_font.render(destination, True, self.colors['text_primary'])
        surface.blit(dest_surface, (x + 130, y + 15))  # Shifted down by 5 pixels
        
        # Draw secondary details (smaller text below destination with more spacing)
        detail_text = arrival.get('detail', '')
        if detail_text:
            detail_surface = self.detail_font.render(detail_text, True, self.colors['text_secondary'])
            surface.blit(detail_surface, (x + 130, y + 50))  # Shifted down by 5 pixels
        
        # Draw arrival time (right side) - matching the real display format
        if time_remaining == "Now":
            time_num = "Now"
            time_unit = ""
        elif time_remaining.endswith('s'):
            time_num = time_remaining
            time_unit = ""
        else:
            # Extract minutes and show "MM" format
            time_num = time_remaining.replace('m', '')
            time_unit = "MM"
        
        # Right-align the time text
        time_surface = self.time_font.render(time_num, True, self.colors['text_primary'])
        time_rect = time_surface.get_rect()
        time_x = self.screen.get_width() - 50 - time_rect.width  # Right-align with 50px margin
        surface.blit(time_surface, (time_x, y + 20))  # Shifted down by 5 pixels
        
        if time_unit:
            unit_surface = self.time_unit_font.render(time_unit, True, self.colors['text_primary'])
            unit_rect = unit_surface.get_rect()
            unit_x = self.screen.get_width() - 50 - unit_rect.width  # Right-align with 50px margin
            surface.blit(unit_surface, (unit_x, y + 45))  # Shifted down by 5 pixels
    
    def draw_display(self, arrivals: List[Dict]):
        """Draw the main display matching the real MTA sign layout"""
        # Fill with dark blue background
        self.screen.fill(self.colors['background'])
        
        # Draw black frame around the display
        frame_rect = pygame.Rect(10, 10, self.screen.get_width() - 20, self.screen.get_height() - 20)
        pygame.draw.rect(self.screen, self.colors['frame'], frame_rect, 3)
        
        # Draw green status light at top center
        status_light_rect = pygame.Rect(self.screen.get_width() // 2 - 5, 15, 10, 10)
        pygame.draw.rect(self.screen, self.colors['status_light'], status_light_rect)
        
        # Draw sign ID in top left (like "468-0-4" in the image)
        sign_id = "MTA-001"
        id_surface = self.detail_font.render(sign_id, True, self.colors['text_white'])
        self.screen.blit(id_surface, (20, 20))
        
        # Draw station name below the sign ID
        station_surface = self.destination_font.render(self.station_name, True, self.colors['text_white'])
        self.screen.blit(station_surface, (20, 45))
        
        # Check if we have any arrivals
        if not arrivals:
            # Draw error message
            error_surface = self.destination_font.render("NO DATA AVAILABLE", True, self.colors['text_white'])
            error_rect = error_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(error_surface, error_rect)
            
            # Draw additional error info
            error_detail = self.detail_font.render("Check MTA API connection", True, self.colors['text_secondary'])
            detail_rect = error_detail.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40))
            self.screen.blit(error_detail, detail_rect)
            pygame.display.flip()
            return
        
        # Draw arrivals in horizontal rows like the real display
        y_start = 80
        y_spacing = 90  # Increased space between rows for better readability
        
        for i, arrival in enumerate(arrivals[:4]):  # Show max 4 arrivals like real display
            y_pos = y_start + (i * y_spacing)
            self.draw_arrival(self.screen, 30, y_pos, arrival, i + 1)
            
            # Draw subtle divider line between entries (except after the last one)
            if i < len(arrivals[:4]) - 1:
                divider_y = y_pos + 88  # Position the divider below the current entry (y_pos + 5 + 80 + 3 = y_pos + 88)
                # Use a more subtle color and thinner line
                pygame.draw.line(self.screen, (50, 80, 120), 
                               (60, divider_y), (self.screen.get_width() - 60, divider_y), 1)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.fullscreen = not self.fullscreen
                    self.setup_display()
    
    def run(self):
        """Main application loop"""
        logger.info("Starting MTA Display...")
        last_update = 0
        
        while self.running:
            current_time = time.time()
            
            # Update data at specified intervals
            if current_time - last_update >= self.refresh_interval:
                logger.info("Updating MTA data...")
                arrivals = self.fetch_mta_data()
                arrivals = self.filter_nearby_stations(arrivals)
                last_update = current_time
            else:
                # Use cached data
                arrivals = getattr(self, 'cached_arrivals', [])
            
            # Cache arrivals for next frame
            self.cached_arrivals = arrivals
            
            # Draw display
            self.draw_display(arrivals)
            
            # Handle events
            self.handle_events()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()
        logger.info("MTA Display stopped.")

def main():
    """Main entry point"""
    try:
        app = MTADisplay()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

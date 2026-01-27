"""
Utility functions for parsing wearable device tracking files
Supports GPX, FIT, and TCX formats from smartwatches and fitness trackers
"""
import gpxpy
import gpxpy.gpx
from fitparse import FitFile
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET

class WearableDataParser:
    """Parse tracking data from wearable devices"""
    
    @staticmethod
    def parse_gpx(file_content: bytes) -> Dict:
        """
        Parse GPX file from devices like Garmin, Strava, etc.
        Returns hiking session data with route coordinates
        """
        try:
            gpx = gpxpy.parse(file_content.decode('utf-8'))
            
            # Extract metadata
            name = gpx.name or "Imported Hike"
            description = gpx.description or ""
            
            # Extract all track points
            all_points = []
            total_distance = 0
            min_elevation = float('inf')
            max_elevation = float('-inf')
            start_time = None
            end_time = None
            
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        all_points.append({
                            'latitude': point.latitude,
                            'longitude': point.longitude,
                            'elevation': point.elevation or 0,
                            'time': point.time
                        })
                        
                        if point.elevation:
                            min_elevation = min(min_elevation, point.elevation)
                            max_elevation = max(max_elevation, point.elevation)
                        
                        if point.time:
                            if not start_time:
                                start_time = point.time
                            end_time = point.time
            
            # Calculate total distance
            total_distance = gpx.length_3d() / 1000  # Convert to km
            
            # Calculate elevation gain
            elevation_gain = max_elevation - min_elevation if min_elevation != float('inf') else 0
            
            # Calculate duration
            duration_hours = 0
            if start_time and end_time:
                duration = end_time - start_time
                duration_hours = duration.total_seconds() / 3600
            
            # Get center point for location
            center_lat = sum(p['latitude'] for p in all_points) / len(all_points) if all_points else 0
            center_lon = sum(p['longitude'] for p in all_points) / len(all_points) if all_points else 0
            
            return {
                'success': True,
                'name': name,
                'description': description,
                'route_coordinates': all_points,
                'total_distance_km': round(total_distance, 2),
                'elevation_gain_m': round(elevation_gain, 2),
                'duration_hours': round(duration_hours, 2),
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'start_time': start_time.isoformat() if start_time else None,
                'end_time': end_time.isoformat() if end_time else None,
                'total_points': len(all_points),
                'source': 'GPX'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"GPX parsing error: {str(e)}"
            }
    
    @staticmethod
    def parse_fit(file_content: bytes) -> Dict:
        """
        Parse FIT file from Garmin watches
        Returns hiking session data with route coordinates
        """
        try:
            fitfile = FitFile(file_content)
            
            # Extract session data
            session_data = None
            for record in fitfile.get_messages('session'):
                session_data = record
                break
            
            # Extract track points
            all_points = []
            start_time = None
            end_time = None
            
            for record in fitfile.get_messages('record'):
                point = {}
                
                for data in record:
                    if data.name == 'position_lat' and data.value is not None:
                        point['latitude'] = data.value * (180 / 2**31)  # Convert semicircles to degrees
                    elif data.name == 'position_long' and data.value is not None:
                        point['longitude'] = data.value * (180 / 2**31)
                    elif data.name == 'altitude' and data.value is not None:
                        point['elevation'] = data.value
                    elif data.name == 'timestamp' and data.value is not None:
                        point['time'] = data.value
                        if not start_time:
                            start_time = data.value
                        end_time = data.value
                
                if 'latitude' in point and 'longitude' in point:
                    all_points.append(point)
            
            # Extract session metrics
            total_distance = 0
            duration_hours = 0
            elevation_gain = 0
            
            if session_data:
                for data in session_data:
                    if data.name == 'total_distance' and data.value is not None:
                        total_distance = data.value / 1000  # Convert to km
                    elif data.name == 'total_elapsed_time' and data.value is not None:
                        duration_hours = data.value / 3600  # Convert to hours
                    elif data.name == 'total_ascent' and data.value is not None:
                        elevation_gain = data.value
            
            # Fallback: calculate distance from points if not in session
            if total_distance == 0 and len(all_points) > 1:
                import math
                R = 6371  # Earth radius in km
                for i in range(1, len(all_points)):
                    lat1, lon1 = all_points[i-1]['latitude'], all_points[i-1]['longitude']
                    lat2, lon2 = all_points[i]['latitude'], all_points[i]['longitude']
                    dlat = math.radians(lat2 - lat1)
                    dlon = math.radians(lon2 - lon1)
                    a = (math.sin(dlat/2) * math.sin(dlat/2) +
                         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                         math.sin(dlon/2) * math.sin(dlon/2))
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    total_distance += R * c
            
            # Fallback: calculate elevation gain from points if not in session
            if elevation_gain == 0:
                elevations = [p.get('elevation', 0) for p in all_points if 'elevation' in p]
                if elevations:
                    elevation_gain = max(elevations) - min(elevations)
            
            # Calculate center point
            center_lat = sum(p['latitude'] for p in all_points) / len(all_points) if all_points else 0
            center_lon = sum(p['longitude'] for p in all_points) / len(all_points) if all_points else 0
            
            return {
                'success': True,
                'name': "Imported Hike",
                'description': "Imported from Garmin device",
                'route_coordinates': all_points,
                'total_distance_km': round(total_distance, 2),
                'elevation_gain_m': round(elevation_gain, 2),
                'duration_hours': round(duration_hours, 2),
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'start_time': start_time.isoformat() if start_time and hasattr(start_time, 'isoformat') else None,
                'end_time': end_time.isoformat() if end_time and hasattr(end_time, 'isoformat') else None,
                'total_points': len(all_points),
                'source': 'FIT'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"FIT parsing error: {str(e)}"
            }
    
    @staticmethod
    def parse_tcx(file_content: bytes) -> Dict:
        """
        Parse TCX file from various devices
        Returns hiking session data with route coordinates
        """
        try:
            root = ET.fromstring(file_content.decode('utf-8'))
            
            # Try multiple namespace variants
            namespaces = [
                {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'},
                {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1'},
                {}  # No namespace fallback
            ]
            
            all_points = []
            start_time = None
            end_time = None
            
            # Try each namespace variant
            for ns in namespaces:
                trackpoints = root.findall('.//tcx:Trackpoint', ns) if ns else root.findall('.//Trackpoint')
                
                if trackpoints:
                    for trackpoint in trackpoints:
                        point = {}
                        
                        # Get position
                        position = trackpoint.find('tcx:Position', ns) if ns else trackpoint.find('Position')
                        if position is not None:
                            lat = position.find('tcx:LatitudeDegrees', ns) if ns else position.find('LatitudeDegrees')
                            lon = position.find('tcx:LongitudeDegrees', ns) if ns else position.find('LongitudeDegrees')
                            if lat is not None and lon is not None and lat.text and lon.text:
                                point['latitude'] = float(lat.text)
                                point['longitude'] = float(lon.text)
                        
                        # Get elevation
                        altitude = trackpoint.find('tcx:AltitudeMeters', ns) if ns else trackpoint.find('AltitudeMeters')
                        if altitude is not None and altitude.text:
                            point['elevation'] = float(altitude.text)
                        
                        # Get time
                        time_elem = trackpoint.find('tcx:Time', ns) if ns else trackpoint.find('Time')
                        if time_elem is not None and time_elem.text:
                            try:
                                point['time'] = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
                                if not start_time:
                                    start_time = point['time']
                                end_time = point['time']
                            except:
                                pass
                        
                        if 'latitude' in point and 'longitude' in point:
                            all_points.append(point)
                    
                    # If we found points, no need to try other namespaces
                    if all_points:
                        break
            
            # Calculate metrics
            total_distance = 0
            if len(all_points) > 1:
                for i in range(1, len(all_points)):
                    # Simple distance calculation
                    lat1, lon1 = all_points[i-1]['latitude'], all_points[i-1]['longitude']
                    lat2, lon2 = all_points[i]['latitude'], all_points[i]['longitude']
                    
                    # Haversine formula (simplified)
                    import math
                    R = 6371  # Earth radius in km
                    dlat = math.radians(lat2 - lat1)
                    dlon = math.radians(lon2 - lon1)
                    a = (math.sin(dlat/2) * math.sin(dlat/2) +
                         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                         math.sin(dlon/2) * math.sin(dlon/2))
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    total_distance += R * c
            
            # Calculate elevation gain
            elevations = [p.get('elevation', 0) for p in all_points if 'elevation' in p]
            elevation_gain = max(elevations) - min(elevations) if elevations else 0
            
            # Calculate duration
            duration_hours = 0
            if start_time and end_time:
                duration = end_time - start_time
                duration_hours = duration.total_seconds() / 3600
            
            # Calculate center point
            center_lat = sum(p['latitude'] for p in all_points) / len(all_points) if all_points else 0
            center_lon = sum(p['longitude'] for p in all_points) / len(all_points) if all_points else 0
            
            return {
                'success': True,
                'name': "Imported Hike",
                'description': "Imported from TCX file",
                'route_coordinates': all_points,
                'total_distance_km': round(total_distance, 2),
                'elevation_gain_m': round(elevation_gain, 2),
                'duration_hours': round(duration_hours, 2),
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'start_time': start_time.isoformat() if start_time else None,
                'end_time': end_time.isoformat() if end_time else None,
                'total_points': len(all_points),
                'source': 'TCX'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"TCX parsing error: {str(e)}"
            }
    
    @staticmethod
    def parse_file(file_content: bytes, file_extension: str) -> Dict:
        """
        Parse wearable device file based on extension
        """
        ext = file_extension.lower().replace('.', '')
        
        if ext == 'gpx':
            return WearableDataParser.parse_gpx(file_content)
        elif ext == 'fit':
            return WearableDataParser.parse_fit(file_content)
        elif ext == 'tcx':
            return WearableDataParser.parse_tcx(file_content)
        else:
            return {
                'success': False,
                'error': f"Unsupported file format: {ext}. Supported formats: GPX, FIT, TCX"
            }

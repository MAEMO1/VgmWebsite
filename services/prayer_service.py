from datetime import date, datetime, timedelta
import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)

class PrayerService:
    """Service for fetching prayer times"""

    def __init__(self):
        self._cache = {}

    def get_prayer_times(self, target_date: date, city: str = "Gent") -> Optional[Dict[str, str]]:
        """Get prayer times for a specific date"""
        try:
            # Check cache first
            cache_key = f"{target_date}_{city}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Get coordinates for Gent
            lat, lng = 51.0543422, 3.7174243

            # Configure API request
            params = {
                'latitude': lat,
                'longitude': lng,
                'method': 13,  # Diyanet method
                'month': target_date.month,
                'year': target_date.year,
                'adjustment': 0,
                'school': 1,  # Hanafi
                'timezonestring': 'Europe/Brussels'
            }

            response = requests.get(
                'http://api.aladhan.com/v1/calendar',
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # Find the specific day
                for day_data in data.get('data', []):
                    day_date = datetime.strptime(
                        day_data['date']['gregorian']['date'],
                        '%d-%m-%Y'
                    ).date()

                    if day_date == target_date:
                        times = day_data['timings']
                        prayer_times = {
                            'fajr': times['Fajr'].split(' ')[0],
                            'sunrise': times['Sunrise'].split(' ')[0],
                            'dhuhr': times['Dhuhr'].split(' ')[0],
                            'asr': times['Asr'].split(' ')[0],
                            'maghrib': times['Maghrib'].split(' ')[0],
                            'isha': times['Isha'].split(' ')[0]
                        }

                        # Cache the result
                        self._cache[cache_key] = prayer_times
                        return prayer_times

            logger.warning(f"No prayer times found for {target_date}")
            return None

        except Exception as e:
            logger.error(f"Error fetching prayer times: {e}", exc_info=True)
            return None

    def get_prayer_times_range(self, start_date: date, end_date: date, 
                           city: str = "Gent") -> Dict[date, Dict[str, str]]:
        """Get prayer times for a date range"""
        prayer_times = {}
        current_date = start_date

        while current_date <= end_date:
            times = self.get_prayer_times(current_date, city)
            if times:
                prayer_times[current_date] = times
            current_date += timedelta(days=1)

        return prayer_times

# Create a singleton instance of the prayer service
_prayer_service = PrayerService()

def get_prayer_times_for_date_range(start_date: date, end_date: date, city: str = "Gent") -> Dict[date, Dict[str, str]]:
    """Get prayer times for a date range using the singleton service instance"""
    return _prayer_service.get_prayer_times_range(start_date, end_date, city)
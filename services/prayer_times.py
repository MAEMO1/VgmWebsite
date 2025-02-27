import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PrayerTimeService:
    """Handles fetching and validation of prayer times from multiple sources"""

    ALADHAN_API_URL = "http://api.aladhan.com/v1/calendar"
    MAWAQIT_BASE_URL = "https://mawaqit.net/api/2.0"

    def __init__(self):
        self.cache = {}  # Simple in-memory cache

    def get_prayer_times_for_range(self, source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range with fallback mechanism
        """
        try:
            logger.info(f"Fetching prayer times for {start_date} to {end_date} using {source}")

            # Check cache first
            cache_key = f"{start_date}_{end_date}_{source}_{city}"
            if cache_key in self.cache:
                logger.info("Returning cached prayer times")
                return self.cache[cache_key]

            # Try primary source
            if source == 'diyanet':
                prayer_times = self._get_aladhan_times(start_date, end_date, city)
                if prayer_times:
                    self.cache[cache_key] = prayer_times
                    return prayer_times
                logger.warning("Aladhan API failed, falling back to Mawaqit")

            # Fallback to Mawaqit
            prayer_times = self._get_mawaqit_api_times(start_date, end_date, city)
            if prayer_times:
                self.cache[cache_key] = prayer_times
                return prayer_times

            return None

        except Exception as e:
            logger.error(f"Error fetching prayer times: {e}", exc_info=True)
            return None

    def _get_aladhan_times(self, start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """Get prayer times from Aladhan API with validation"""
        try:
            # Precise coordinates for Gent
            latitude = 51.0543422
            longitude = 3.7174243

            prayer_times = {}
            current_date = start_date

            while current_date <= end_date:
                params = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'method': 13,  # Diyanet İşleri Başkanlığı
                    'month': current_date.month,
                    'year': current_date.year,
                    'adjustment': 0,
                    'school': 1,  # Hanafi
                    'timezonestring': 'Europe/Brussels'
                }

                response = requests.get(self.ALADHAN_API_URL, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    for day_data in data.get('data', []):
                        try:
                            day_date = datetime.strptime(
                                day_data['date']['gregorian']['date'],
                                '%d-%m-%Y'
                            ).date()

                            if start_date <= day_date <= end_date:
                                times = day_data['timings']
                                prayer_times[day_date] = self._validate_and_clean_times({
                                    'fajr': times['Fajr'].split(' ')[0],
                                    'sunrise': times['Sunrise'].split(' ')[0],
                                    'dhuhr': times['Dhuhr'].split(' ')[0],
                                    'asr': times['Asr'].split(' ')[0],
                                    'maghrib': times['Maghrib'].split(' ')[0],
                                    'isha': times['Isha'].split(' ')[0]
                                })

                        except Exception as e:
                            logger.error(f"Error processing day data: {e}")
                            continue

                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

            return prayer_times if prayer_times else None

        except Exception as e:
            logger.error(f"Error with Aladhan API: {e}", exc_info=True)
            return None

    def _get_mawaqit_api_times(self, start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """Get prayer times from Mawaqit API with validation"""
        try:
            # Get mosque UUID
            search_response = requests.get(
                f"{self.MAWAQIT_BASE_URL}/mosque/search",
                params={'q': city, 'limit': 1},
                headers={'Accept': 'application/json'},
                timeout=10
            )

            if search_response.status_code != 200:
                return None

            mosque_data = search_response.json()
            if not mosque_data.get('mosques'):
                return None

            mosque_uuid = mosque_data['mosques'][0].get('uuid')
            if not mosque_uuid:
                return None

            # Get prayer times
            times_response = requests.get(
                f"{self.MAWAQIT_BASE_URL}/mosque/{mosque_uuid}/prayers",
                params={
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                headers={'Accept': 'application/json'},
                timeout=10
            )

            if times_response.status_code != 200:
                return None

            times_data = times_response.json()
            prayer_times = {}

            for day_data in times_data.get('prayers', []):
                try:
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                    prayer_times[day_date] = self._validate_and_clean_times({
                        'fajr': day_data['fajr'],
                        'sunrise': day_data['sunrise'],
                        'dhuhr': day_data['dhuhr'],
                        'asr': day_data['asr'],
                        'maghrib': day_data['maghrib'],
                        'isha': day_data['isha']
                    })
                except Exception as e:
                    logger.error(f"Error processing Mawaqit day data: {e}")
                    continue

            return prayer_times if prayer_times else None

        except Exception as e:
            logger.error(f"Error with Mawaqit API: {e}", exc_info=True)
            return None

    def _validate_and_clean_times(self, times: Dict[str, str]) -> Dict[str, str]:
        """Validate and clean prayer times"""
        cleaned_times = {}
        for prayer, time_str in times.items():
            try:
                # Remove timezone indicators if present
                time_str = time_str.split(' ')[0]
                # Validate time format
                datetime.strptime(time_str, '%H:%M')
                cleaned_times[prayer] = time_str
            except Exception as e:
                logger.error(f"Invalid time format for {prayer}: {time_str}")
                cleaned_times[prayer] = None

        return cleaned_times

    def get_prayer_times_batch(self, source: str, dates: List[date], prayer_name: str, city: str = "Gent") -> Dict[date, Optional[str]]:
        """Get prayer times for multiple dates efficiently"""
        if not dates:
            return {}

        result = {}
        start_date = min(dates)
        end_date = max(dates)

        # Get all prayer times for the date range
        all_times = self.get_prayer_times_for_range(source, start_date, end_date, city)

        # Extract specific prayer times for requested dates
        for request_date in dates:
            if all_times and request_date in all_times:
                result[request_date] = all_times[request_date].get(prayer_name.lower())
            else:
                result[request_date] = None

        return result
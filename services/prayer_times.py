import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging

class PrayerTimeService:
    MAWAQIT_API_URL = "https://api.mawaqit.net/api/v1"

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range
        """
        if source == "mawaqit":
            return PrayerTimeService._get_mawaqit_times_range(start_date, end_date, city)
        return None

    @staticmethod
    def _get_mawaqit_times_range(start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times from Mawaqit API for a date range
        """
        try:
            api_key = os.environ.get("MAWAQIT_API_KEY")
            if not api_key:
                logging.error("Mawaqit API key not found in environment variables")
                return None

            # Mawaqit API endpoint for prayer times
            response = requests.get(
                f"{PrayerTimeService.MAWAQIT_API_URL}/prayer-times",
                params={
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                    "city": city,
                    "country": "Belgium"
                },
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )

            logging.info(f"Mawaqit API Response: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    logging.info(f"Mawaqit API Data: {data}")
                    prayer_times = {}

                    # Process each day's prayer times based on actual Mawaqit API format
                    for day_data in data.get('prayer_times', []):
                        try:
                            day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                            prayer_times[day_date] = {
                                'fajr': day_data.get('fajr'),
                                'sunrise': day_data.get('sunrise'),
                                'dhuhr': day_data.get('dhuhr'),
                                'asr': day_data.get('asr'),
                                'maghrib': day_data.get('maghrib'),
                                'isha': day_data.get('isha')
                            }
                        except KeyError as ke:
                            logging.error(f"Missing key in day data: {ke}")
                            continue
                        except ValueError as ve:
                            logging.error(f"Invalid date format: {ve}")
                            continue

                    if prayer_times:
                        return prayer_times
                    logging.error("No prayer times found in response")
                    return None

                except Exception as je:
                    logging.error(f"Error parsing JSON response: {je}")
                    return None
            else:
                logging.error(f"Mawaqit API error: {response.status_code}")
                if response.content:
                    logging.error(f"Error response: {response.content}")
                return None

        except Exception as e:
            logging.error(f"Error fetching Mawaqit times: {e}")
            return None

    @staticmethod
    def get_prayer_time(source: str, prayer_date: date, prayer_name: str, city: str = "Gent") -> Optional[str]:
        """
        Get specific prayer time for a single date
        """
        times = PrayerTimeService.get_prayer_times_for_range(source, prayer_date, prayer_date, city)
        if times and prayer_date in times and prayer_name.lower() in times[prayer_date]:
            return times[prayer_date][prayer_name.lower()]
        return None

    @staticmethod
    def get_prayer_times_batch(source: str, dates: List[date], prayer_name: str, city: str = "Gent") -> Dict[date, Optional[str]]:
        """
        Get specific prayer times for multiple dates efficiently
        """
        if not dates:
            return {}

        # Sort dates and get range
        sorted_dates = sorted(dates)
        start_date = sorted_dates[0]
        end_date = sorted_dates[-1]

        # Fetch all times in range
        all_times = PrayerTimeService.get_prayer_times_for_range(source, start_date, end_date, city)

        # Extract requested prayer times for specified dates
        result = {}
        for request_date in dates:
            if all_times and request_date in all_times:
                result[request_date] = all_times[request_date].get(prayer_name.lower())
            else:
                result[request_date] = None

        if None in result.values():
            logging.error(f"Missing prayer times for dates: {[d for d, t in result.items() if t is None]}")

        return result
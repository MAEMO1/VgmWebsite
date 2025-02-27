import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List

class PrayerTimeService:
    MAWAQIT_API_URL = "https://api.mawaqit.net/api/v1"

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range
        """
        if source == "mawaqit":
            return PrayerTimeService._get_mawaqit_times_range(start_date, end_date, city)
        elif source == "diyanet":
            return PrayerTimeService._get_diyanet_times_range(start_date, end_date, city)
        return None

    @staticmethod
    def _get_mawaqit_times_range(start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times from Mawaqit API for a date range
        """
        try:
            # Calculate number of days
            days = (end_date - start_date).days + 1

            # Example API endpoint - replace with actual Mawaqit API
            response = requests.get(
                f"{PrayerTimeService.MAWAQIT_API_URL}/prayer-times",
                params={
                    "city": city,
                    "country": "Belgium",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                headers={
                    "Accept": "application/json"
                }
            )

            if response.status_code == 200:
                data = response.json()
                prayer_times = {}

                # Process each day's prayer times
                for day_data in data['prayer_times']:
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                    prayer_times[day_date] = {
                        'fajr': day_data['fajr'],
                        'sunrise': day_data['sunrise'],
                        'dhuhr': day_data['dhuhr'],
                        'asr': day_data['asr'],
                        'maghrib': day_data['maghrib'],
                        'isha': day_data['isha']
                    }
                return prayer_times
            else:
                print(f"Mawaqit API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching Mawaqit times: {e}")
            return None

    @staticmethod
    def _get_diyanet_times_range(start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times from Diyanet API for a date range
        """
        try:
            # Calculate number of days
            days = (end_date - start_date).days + 1

            # Example API endpoint - replace with actual Diyanet API
            response = requests.get(
                f"https://api.diyanet.gov.tr/prayer-times",
                params={
                    "city": city,
                    "country": "Belgium",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "days": days
                }
            )

            if response.status_code == 200:
                data = response.json()
                prayer_times = {}

                # Process each day's prayer times
                for day_data in data:
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                    prayer_times[day_date] = {
                        'fajr': day_data['fajr'],
                        'sunrise': day_data['sunrise'],
                        'dhuhr': day_data['dhuhr'],
                        'asr': day_data['asr'],
                        'maghrib': day_data['maghrib'],
                        'isha': day_data['isha']
                    }
                return prayer_times

        except Exception as e:
            print(f"Error fetching Diyanet times: {e}")
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

        return result
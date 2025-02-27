import os
import requests
from datetime import datetime, date
from typing import Dict, Optional

class PrayerTimeService:
    @staticmethod
    def get_prayer_times(source: str, date: date, city: str = "Gent") -> Optional[Dict]:
        """
        Fetch prayer times from the specified source
        """
        if source == "mawaqeet":
            return PrayerTimeService._get_mawaqeet_times(date, city)
        elif source == "diyanet":
            return PrayerTimeService._get_diyanet_times(date, city)
        return None

    @staticmethod
    def _get_mawaqeet_times(date: date, city: str) -> Optional[Dict]:
        """
        Fetch prayer times from Mawaqeet API
        """
        try:
            # Example API endpoint - replace with actual Mawaqeet API
            response = requests.get(
                f"https://api.mawaqeet.org/prayer-times",
                params={
                    "city": city,
                    "country": "Belgium",
                    "date": date.strftime("%Y-%m-%d")
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "fajr": data["fajr"],
                    "sunrise": data["sunrise"],
                    "dhuhr": data["dhuhr"],
                    "asr": data["asr"],
                    "maghrib": data["maghrib"],
                    "isha": data["isha"]
                }
        except Exception as e:
            print(f"Error fetching Mawaqeet times: {e}")
        return None

    @staticmethod
    def _get_diyanet_times(date: date, city: str) -> Optional[Dict]:
        """
        Fetch prayer times from Diyanet API
        """
        try:
            # Example API endpoint - replace with actual Diyanet API
            response = requests.get(
                f"https://api.diyanet.gov.tr/prayer-times",
                params={
                    "city": city,
                    "country": "Belgium",
                    "date": date.strftime("%Y-%m-%d")
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "fajr": data["fajr"],
                    "sunrise": data["sunrise"],
                    "dhuhr": data["dhuhr"],
                    "asr": data["asr"],
                    "maghrib": data["maghrib"],
                    "isha": data["isha"]
                }
        except Exception as e:
            print(f"Error fetching Diyanet times: {e}")
        return None

    @staticmethod
    def get_prayer_time(source: str, date: date, prayer_name: str, city: str = "Gent") -> Optional[str]:
        """
        Get specific prayer time
        """
        times = PrayerTimeService.get_prayer_times(source, date, city)
        if times and prayer_name.lower() in times:
            return times[prayer_name.lower()]
        return None

import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging

class PrayerTimeService:
    MAWAQIT_API_URL = "https://mawaqit.net/api/2.0"

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range
        """
        try:
            # We need to get the mosque ID from Mawaqit first
            search_response = requests.get(
                f"{PrayerTimeService.MAWAQIT_API_URL}/mosque/search",
                params={
                    "q": "Gent",  # Search for mosques in Gent
                    "limit": 1    # Get first result
                }
            )

            if search_response.status_code != 200:
                logging.error(f"Failed to search for mosque: {search_response.status_code}")
                return None

            search_data = search_response.json()
            if not search_data or 'mosques' not in search_data or not search_data['mosques']:
                logging.error("No mosque found in search results")
                return None

            mosque_id = search_data['mosques'][0].get('uuid')
            if not mosque_id:
                logging.error("No mosque ID found in search result")
                return None

            # Calculate the number of days
            days = (end_date - start_date).days + 1

            request_params = {
                "date": start_date.strftime("%Y-%m-%d"),
                "days": days
            }

            logging.info(f"Calling Mawaqit API for mosque {mosque_id} with parameters: {request_params}")
            api_url = f"{PrayerTimeService.MAWAQIT_API_URL}/mosque/{mosque_id}/prayer-times"
            logging.info(f"API URL: {api_url}")

            response = requests.get(api_url, params=request_params)
            logging.info(f"Mawaqit API Response Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    logging.debug(f"Full API Response: {data}")
                    prayer_times = {}

                    # Process each day's prayer times
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
                            logging.debug(f"Processed prayer times for {day_date}: {prayer_times[day_date]}")
                        except KeyError as ke:
                            logging.error(f"Missing key in day data: {ke}")
                            logging.error(f"Day data content: {day_data}")
                            continue
                        except ValueError as ve:
                            logging.error(f"Invalid date format: {ve}")
                            logging.error(f"Date string received: {day_data.get('date')}")
                            continue

                    if prayer_times:
                        return prayer_times
                    logging.error("No prayer times found in response")
                    return None

                except Exception as je:
                    logging.error(f"Error parsing JSON response: {je}")
                    logging.error(f"Raw response content: {response.content}")
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
        logging.info(f"Fetching prayer time for {prayer_date}, prayer: {prayer_name}")
        times = PrayerTimeService.get_prayer_times_for_range(source, prayer_date, prayer_date, city)
        if times and prayer_date in times:
            prayer_times = times[prayer_date]
            if prayer_name.lower() in prayer_times and prayer_times[prayer_name.lower()]:
                return prayer_times[prayer_name.lower()]
            logging.error(f"Prayer {prayer_name} not found in times: {prayer_times}")
        return None

    @staticmethod
    def get_prayer_times_batch(source: str, dates: List[date], prayer_name: str, city: str = "Gent") -> Dict[date, Optional[str]]:
        """
        Get specific prayer times for multiple dates efficiently
        """
        if not dates:
            return {}

        # Process dates in smaller batches to avoid overwhelming the API
        batch_size = 30  # Process 30 days at a time
        result = {}

        for i in range(0, len(dates), batch_size):
            batch_dates = dates[i:i + batch_size]
            start_date = min(batch_dates)
            end_date = max(batch_dates)

            logging.info(f"Processing batch from {start_date} to {end_date}")

            # Fetch times for this batch
            batch_times = PrayerTimeService.get_prayer_times_for_range(source, start_date, end_date, city)

            # Extract requested prayer times for specified dates in this batch
            for request_date in batch_dates:
                if batch_times and request_date in batch_times:
                    prayer_times = batch_times[request_date]
                    result[request_date] = prayer_times.get(prayer_name.lower())
                    if result[request_date] is None:
                        logging.error(f"Prayer time {prayer_name} not found for date {request_date}")
                else:
                    logging.error(f"No prayer times found for date {request_date}")
                    result[request_date] = None

        if None in result.values():
            missing_dates = [d.strftime("%Y-%m-%d") for d, t in result.items() if t is None]
            logging.error(f"Missing prayer times for dates: {missing_dates}")

        return result
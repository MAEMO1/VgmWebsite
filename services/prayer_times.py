import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging

class PrayerTimeService:
    MAWAQIT_API_URL = "https://www.mawaqit.net/api/v2"

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range
        """
        try:
            # First get the mosque UUID using the search endpoint
            logging.info(f"Searching for mosque in {city}")
            search_url = f"{PrayerTimeService.MAWAQIT_API_URL}/search"
            search_params = {
                "query": city,
                "type": "mosques",
                "country": "BE",
                "limit": 1
            }

            logging.info(f"Search request URL: {search_url}")
            logging.info(f"Search parameters: {search_params}")

            # Add headers to specify JSON response
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            search_response = requests.get(search_url, params=search_params, headers=headers)
            logging.info(f"Search response status: {search_response.status_code}")

            # Log raw response for debugging
            logging.debug(f"Raw search response: {search_response.text}")

            if search_response.status_code != 200:
                logging.error(f"Mosque search failed: {search_response.content}")
                return None

            try:
                search_data = search_response.json()
                logging.debug(f"Search response data: {search_data}")
            except Exception as je:
                logging.error(f"Failed to parse search response JSON: {je}")
                logging.error(f"Raw response content: {search_response.text}")
                return None

            if not search_data or not search_data.get('data'):
                logging.error("No mosques found in search results")
                return None

            mosque = search_data['data'][0]
            mosque_uuid = mosque.get('uuid')

            if not mosque_uuid:
                logging.error("No mosque UUID found in search result")
                return None

            logging.info(f"Found mosque UUID: {mosque_uuid}")

            # Now get prayer times for this mosque
            days = (end_date - start_date).days + 1
            times_url = f"{PrayerTimeService.MAWAQIT_API_URL}/mosque/{mosque_uuid}/prayer-times"
            times_params = {
                "date": start_date.strftime("%Y-%m-%d"),
                "days": days
            }

            logging.info(f"Prayer times request URL: {times_url}")
            logging.info(f"Prayer times parameters: {times_params}")

            times_response = requests.get(times_url, params=times_params, headers=headers)
            logging.info(f"Prayer times response status: {times_response.status_code}")

            # Log raw response for debugging
            logging.debug(f"Raw prayer times response: {times_response.text}")

            if times_response.status_code != 200:
                logging.error(f"Failed to get prayer times: {times_response.content}")
                return None

            try:
                data = times_response.json()
                logging.debug(f"Prayer times response data: {data}")
            except Exception as je:
                logging.error(f"Failed to parse prayer times JSON: {je}")
                logging.error(f"Raw response content: {times_response.text}")
                return None

            prayer_times = {}
            for day_data in data.get('data', []):
                try:
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                    times = day_data.get('times', {})
                    prayer_times[day_date] = {
                        'fajr': times.get('fajr'),
                        'sunrise': times.get('sunrise'),
                        'dhuhr': times.get('dhuhr'),
                        'asr': times.get('asr'),
                        'maghrib': times.get('maghrib'),
                        'isha': times.get('isha')
                    }
                    logging.debug(f"Processed times for {day_date}: {prayer_times[day_date]}")
                except Exception as e:
                    logging.error(f"Error processing day data: {e}")
                    logging.error(f"Problematic day data: {day_data}")
                    continue

            if not prayer_times:
                logging.error("No prayer times found in response")
                return None

            return prayer_times

        except Exception as e:
            logging.error(f"Error fetching prayer times: {e}")
            logging.error(f"Stack trace:", exc_info=True)
            return None

    @staticmethod
    def get_prayer_time(source: str, prayer_date: date, prayer_name: str, city: str = "Gent") -> Optional[str]:
        """
        Get specific prayer time for a single date
        """
        logging.info(f"Getting {prayer_name} time for {prayer_date}")
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
        batch_size = 7  # Process a week at a time
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
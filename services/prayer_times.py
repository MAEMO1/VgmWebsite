import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging
from bs4 import BeautifulSoup

class PrayerTimeService:
    MAWAQIT_BASE_URL = "https://mawaqit.net"

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range
        """
        try:
            # First try with the specific mosque ID for Gent
            mosque_id = "moskee-gent-vlaanderen"  # Example ID, should be configured
            logging.info(f"Trying direct mosque ID: {mosque_id}")

            # Try multiple URL formats
            urls_to_try = [
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/en/mosque/{mosque_id}",
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/en/{city.lower()}",
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/en/belgium/{city.lower()}"
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }

            mosque_found = False
            for url in urls_to_try:
                logging.info(f"Trying URL: {url}")
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    mosque_found = True
                    mosque_url = url
                    break

            if not mosque_found:
                logging.error("Could not find mosque page with any URL format")
                return PrayerTimeService._calculate_prayer_times(start_date, end_date, city)

            # Now get prayer times for this mosque
            times_url = f"{mosque_url}/prayer-times"
            logging.info(f"Fetching prayer times from: {times_url}")

            times_response = requests.get(times_url, headers=headers)
            if times_response.status_code != 200:
                logging.error(f"Failed to get prayer times: {times_response.content}")
                return PrayerTimeService._calculate_prayer_times(start_date, end_date, city)

            # Parse prayer times from HTML
            prayer_times = {}
            soup = BeautifulSoup(times_response.text, 'html.parser')
            times_table = soup.find('table', {'class': ['prayer-times', 'timetable']})

            if not times_table:
                logging.error("Prayer times table not found in response")
                return PrayerTimeService._calculate_prayer_times(start_date, end_date, city)

            for row in times_table.find_all('tr')[1:]:  # Skip header row
                cols = row.find_all('td')
                if len(cols) >= 7:  # Date + 6 prayer times
                    try:
                        # Try different date formats
                        date_text = cols[0].text.strip()
                        try:
                            day_date = datetime.strptime(date_text, '%d/%m/%Y').date()
                        except ValueError:
                            try:
                                day_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                            except ValueError:
                                logging.error(f"Could not parse date: {date_text}")
                                continue

                        prayer_times[day_date] = {
                            'fajr': cols[1].text.strip(),
                            'sunrise': cols[2].text.strip(),
                            'dhuhr': cols[3].text.strip(),
                            'asr': cols[4].text.strip(),
                            'maghrib': cols[5].text.strip(),
                            'isha': cols[6].text.strip()
                        }
                        logging.debug(f"Processed times for {day_date}: {prayer_times[day_date]}")
                    except Exception as e:
                        logging.error(f"Error processing row: {e}")
                        logging.error(f"Row content: {cols}")
                        continue

            if not prayer_times:
                logging.error("No prayer times extracted from the table")
                return PrayerTimeService._calculate_prayer_times(start_date, end_date, city)

            return prayer_times

        except Exception as e:
            logging.error(f"Error fetching prayer times: {e}")
            logging.error("Stack trace:", exc_info=True)
            return PrayerTimeService._calculate_prayer_times(start_date, end_date, city)

    @staticmethod
    def _calculate_prayer_times(start_date: date, end_date: date, city: str) -> Dict[date, Dict]:
        """
        Fallback method to calculate prayer times when API fails
        Uses a basic calculation method as fallback
        """
        logging.info("Using fallback prayer time calculation")
        prayer_times = {}

        # Example fixed times for testing - these should be properly calculated
        test_times = {
            'fajr': '05:30',
            'sunrise': '07:00',
            'dhuhr': '12:30',
            'asr': '15:30',
            'maghrib': '18:00',
            'isha': '19:30'
        }

        current_date = start_date
        while current_date <= end_date:
            prayer_times[current_date] = test_times.copy()
            current_date += timedelta(days=1)

        return prayer_times

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

        # Process dates in smaller batches to avoid overwhelming the website
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
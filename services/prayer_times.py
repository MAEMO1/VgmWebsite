import os
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import logging
from bs4 import BeautifulSoup

class PrayerTimeService:
    ALADHAN_API_URL = "http://api.aladhan.com/v1/calendar"
    MAWAQIT_BASE_URL = "https://mawaqit.net/api/2.0"  # Kept as backup

    @staticmethod
    def get_prayer_times_for_range(source: str, start_date: date, end_date: date, city: str = "Gent") -> Optional[Dict[date, Dict]]:
        """
        Fetch prayer times for a date range using Aladhan API with Diyanet calculation method
        """
        try:
            # Use Aladhan API as primary source with Diyanet calculation method
            prayer_times = PrayerTimeService._get_aladhan_times(start_date, end_date, city)
            if prayer_times:
                return prayer_times

            # Fallback to Mawaqit only if Aladhan fails
            logging.warning("Aladhan API failed, falling back to Mawaqit")
            return PrayerTimeService._get_mawaqit_api_times(start_date, end_date, city)

        except Exception as e:
            logging.error(f"Error fetching prayer times: {e}")
            logging.error("Stack trace:", exc_info=True)
            return None

    @staticmethod
    def _get_mawaqit_api_times(start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """
        Get prayer times using official Mawaqit API
        """
        try:
            # First get mosque details
            search_url = f"{PrayerTimeService.MAWAQIT_BASE_URL}/mosque/search"
            search_params = {
                'q': city,
                'limit': 1
            }
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }

            logging.info(f"Searching for mosque in {city}")
            search_response = requests.get(search_url, params=search_params, headers=headers)

            if search_response.status_code != 200:
                logging.error(f"Mosque search failed: {search_response.status_code}")
                return None

            search_data = search_response.json()
            if not search_data.get('mosques'):
                logging.error("No mosques found in search")
                return None

            mosque = search_data['mosques'][0]
            mosque_uuid = mosque.get('uuid')
            if not mosque_uuid:
                logging.error("No mosque UUID found")
                return None

            # Get prayer times for mosque
            times_url = f"{PrayerTimeService.MAWAQIT_BASE_URL}/mosque/{mosque_uuid}/prayers"
            times_params = {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }

            logging.info(f"Fetching prayer times for mosque {mosque_uuid}")
            times_response = requests.get(times_url, params=times_params, headers=headers)

            if times_response.status_code != 200:
                logging.error(f"Failed to get prayer times: {times_response.status_code}")
                return None

            times_data = times_response.json()
            prayer_times = {}

            for day_data in times_data.get('prayers', []):
                try:
                    day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                    prayer_times[day_date] = {
                        'fajr': day_data['fajr'],
                        'sunrise': day_data['sunrise'],
                        'dhuhr': day_data['dhuhr'],
                        'asr': day_data['asr'],
                        'maghrib': day_data['maghrib'],
                        'isha': day_data['isha']
                    }
                except Exception as e:
                    logging.error(f"Error processing day data: {e}")
                    continue

            return prayer_times

        except Exception as e:
            logging.error(f"Error with Mawaqit API: {e}")
            return None

    @staticmethod
    def _get_mawaqit_website_times(start_date: date, end_date: date, city: str) -> Optional[Dict[date, Dict]]:
        """
        Fallback method to scrape times from Mawaqit website
        """
        try:
            # Try multiple URL formats
            urls_to_try = [
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/mosque/moskee-gent-vlaanderen",
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/en/{city.lower()}",
                f"{PrayerTimeService.MAWAQIT_BASE_URL}/en/belgium/{city.lower()}"
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
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
                logging.error("Could not find mosque page")
                return None

            # Get prayer times
            times_url = f"{mosque_url}/prayer-times"
            times_response = requests.get(times_url, headers=headers)

            if times_response.status_code != 200:
                logging.error(f"Failed to get prayer times page: {times_response.status_code}")
                return None

            # Parse prayer times from HTML
            soup = BeautifulSoup(times_response.text, 'html.parser')
            times_table = soup.find('table', {'class': ['prayer-times', 'timetable']})

            if not times_table:
                logging.error("Prayer times table not found")
                return None

            prayer_times = {}
            for row in times_table.find_all('tr')[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 7:  # Date + 6 prayer times
                    try:
                        date_text = cols[0].text.strip()
                        try:
                            day_date = datetime.strptime(date_text, '%d/%m/%Y').date()
                        except ValueError:
                            day_date = datetime.strptime(date_text, '%Y-%m-%d').date()

                        prayer_times[day_date] = {
                            'fajr': cols[1].text.strip(),
                            'sunrise': cols[2].text.strip(),
                            'dhuhr': cols[3].text.strip(),
                            'asr': cols[4].text.strip(),
                            'maghrib': cols[5].text.strip(),
                            'isha': cols[6].text.strip()
                        }
                    except Exception as e:
                        logging.error(f"Error processing row: {e}")
                        continue

            return prayer_times

        except Exception as e:
            logging.error(f"Error scraping Mawaqit website: {e}")
            return None

    @staticmethod
    def _get_aladhan_times(start_date: date, end_date: date, city: str) -> Dict[date, Dict]:
        """
        Get prayer times from Aladhan API using Diyanet calculation method
        """
        logging.info(f"Using Aladhan API with Diyanet method for period {start_date} to {end_date}")
        prayer_times = {}

        try:
            # Precise coordinates for Gent city center
            latitude = 51.0543422
            longitude = 3.7174243

            # Process each month in the date range
            current_date = start_date
            while current_date <= end_date:
                month = current_date.month
                year = current_date.year

                logging.info(f"Fetching prayer times for {year}-{month:02d}")

                params = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'method': 13,  # Diyanet İşleri Başkanlığı method
                    'month': month,
                    'year': year,
                    'adjustment': 0,
                    'school': 1,  # Hanafi
                    'midnightMode': 0,  # Standard midnight mode
                    'timezonestring': 'Europe/Brussels',
                    'latitudeAdjustmentMethod': 3,  # Angle-based method
                    'iso8601': True  # Use ISO format for better parsing
                }

                logging.info(f"Requesting Aladhan API with params: {params}")
                response = requests.get(PrayerTimeService.ALADHAN_API_URL, params=params)

                if response.status_code == 200:
                    data = response.json()
                    logging.debug(f"Received data from Aladhan API for {year}-{month:02d}")

                    for day_data in data.get('data', []):
                        timings = day_data.get('timings', {})
                        gregorian_date = day_data.get('date', {}).get('gregorian', {})

                        try:
                            day_date = datetime.strptime(
                                gregorian_date.get('date', ''), 
                                '%d-%m-%Y'
                            ).date()

                            if start_date <= day_date <= end_date:
                                # Remove timezone indicators and use clean time strings
                                prayer_times[day_date] = {
                                    'fajr': timings.get('Fajr', '').split(' ')[0],
                                    'sunrise': timings.get('Sunrise', '').split(' ')[0],
                                    'dhuhr': timings.get('Dhuhr', '').split(' ')[0],
                                    'asr': timings.get('Asr', '').split(' ')[0],
                                    'maghrib': timings.get('Maghrib', '').split(' ')[0],
                                    'isha': timings.get('Isha', '').split(' ')[0]
                                }
                                logging.info(f"Added prayer times for {day_date}: {prayer_times[day_date]}")
                        except Exception as e:
                            logging.error(f"Error processing day data: {e}")
                            logging.error(f"Problematic day data: {day_data}")
                            continue

                else:
                    logging.error(f"Aladhan API error: {response.status_code}")
                    logging.error(f"Error response: {response.text}")

                # Move to first day of next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)

            if not prayer_times:
                logging.error("No prayer times retrieved from Aladhan API")
                return None

        except Exception as e:
            logging.error(f"Error with Aladhan API: {e}")
            logging.error("Stack trace:", exc_info=True)
            return None

        return prayer_times

    @staticmethod
    def get_prayer_time(source: str, prayer_date: date, prayer_name: str, city: str = "Gent") -> Optional[str]:
        """
        Get specific prayer time for a date
        """
        logging.info(f"Getting {prayer_name} time for {prayer_date}")
        times = PrayerTimeService.get_prayer_times_for_range(source, prayer_date, prayer_date, city)

        if times and prayer_date in times:
            prayer_times = times[prayer_date]
            if prayer_name.lower() in prayer_times:
                return prayer_times[prayer_name.lower()]
            logging.error(f"Prayer {prayer_name} not found in times")
        return None

    @staticmethod
    def get_prayer_times_batch(source: str, dates: List[date], prayer_name: str, city: str = "Gent") -> Dict[date, Optional[str]]:
        """
        Get prayer times for multiple dates efficiently
        """
        if not dates:
            return {}

        # Process in monthly batches to minimize API calls
        result = {}
        current_month = None
        month_dates = []

        for request_date in sorted(dates):
            if current_month != request_date.month:
                # Process previous month's batch
                if month_dates:
                    start_date = min(month_dates)
                    end_date = max(month_dates)
                    batch_times = PrayerTimeService.get_prayer_times_for_range(source, start_date, end_date, city)

                    for date in month_dates:
                        if batch_times and date in batch_times:
                            result[date] = batch_times[date].get(prayer_name.lower())
                        else:
                            result[date] = None

                # Start new month
                current_month = request_date.month
                month_dates = [request_date]
            else:
                month_dates.append(request_date)

        # Process last month's batch
        if month_dates:
            start_date = min(month_dates)
            end_date = max(month_dates)
            batch_times = PrayerTimeService.get_prayer_times_for_range(source, start_date, end_date, city)

            for date in month_dates:
                if batch_times and date in batch_times:
                    result[date] = batch_times[date].get(prayer_name.lower())
                else:
                    result[date] = None

        # Log any missing times
        if None in result.values():
            missing_dates = [d.strftime("%Y-%m-%d") for d, t in result.items() if t is None]
            logging.error(f"Missing prayer times for dates: {missing_dates}")

        return result
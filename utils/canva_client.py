import os
import logging
import requests
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CanvaClient:
    """Client for interacting with the Canva API"""

    def __init__(self):
        self.api_key = os.environ.get('CANVA_API_KEY')
        self.api_secret = os.environ.get('CANVA_API_SECRET')
        self.base_url = 'https://api.canva.com/v1'
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create an authenticated session for API requests"""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        return session

    def get_brand_resources(self) -> List[Dict]:
        """Fetch brand resources from Canva"""
        try:
            response = self.session.get(f'{self.base_url}/brands/resources')
            response.raise_for_status()
            return response.json().get('resources', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching brand resources: {e}")
            return []

    def get_design(self, design_id: str) -> Optional[Dict]:
        """Fetch a specific design by ID"""
        try:
            response = self.session.get(f'{self.base_url}/designs/{design_id}')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching design {design_id}: {e}")
            return None

    def get_designs(self, limit: int = 10) -> List[Dict]:
        """Fetch recent designs"""
        try:
            response = self.session.get(
                f'{self.base_url}/designs',
                params={'limit': limit}
            )
            response.raise_for_status()
            return response.json().get('designs', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching designs: {e}")
            return []

    def create_calendar_design(self, title: str, month: int, year: int, events: List[Dict]) -> Optional[Dict]:
        """Create a new calendar design for a specific month

        Args:
            title: Title for the calendar design
            month: Month number (1-12)
            year: Year number
            events: List of events with dates and details

        Returns:
            Design details if successful, None otherwise
        """
        try:
            # Format for Canva's design API
            calendar_data = {
                'title': title,
                'type': 'CALENDAR',
                'brandId': self.get_brand_id(),  # Get default brand
                'data': {
                    'month': month,
                    'year': year,
                    'events': events,
                    'format': 'A4',
                    'orientation': 'landscape'
                }
            }

            response = self.session.post(
                f'{self.base_url}/designs',
                json=calendar_data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error creating calendar design: {e}")
            return None

    def get_brand_id(self) -> Optional[str]:
        """Get the default brand ID for the account"""
        brands = self.get_brand_resources()
        return brands[0]['id'] if brands else None

# Initialize the client
canva_client = CanvaClient()
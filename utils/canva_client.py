import os
import logging
import requests
from typing import Optional, Dict, List

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

# Initialize the client
canva_client = CanvaClient()

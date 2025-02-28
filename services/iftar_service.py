from datetime import date, datetime, timedelta
import logging
from typing import List, Dict, Optional
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

class IfterService:
    """Service class for handling iftar events"""

    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_events_for_period(self, start_date: date, end_date: date, 
                            mosque_id: Optional[int] = None,
                            family_only: bool = False) -> List[Dict]:
        """Get filtered iftar events for a specific period"""
        from models import IfterEvent

        try:
            logger.info(f"Fetching events from {start_date} to {end_date}")

            # Build base query
            query = IfterEvent.query.filter(
                IfterEvent.date >= start_date,
                IfterEvent.date <= end_date
            )

            # Apply filters
            if mosque_id:
                query = query.filter(IfterEvent.mosque_id == mosque_id)
            if family_only:
                query = query.filter(IfterEvent.is_family_friendly == True)

            # Execute query
            events = query.order_by(IfterEvent.date, IfterEvent.start_time).all()
            logger.info(f"Found {len(events)} events")

            # Convert to dictionary format
            return [event.to_dict() for event in events]

        except Exception as e:
            logger.error(f"Error fetching events: {e}", exc_info=True)
            return []

    def get_event_by_id(self, event_id: int) -> Optional[Dict]:
        """Get single event by ID"""
        from models import IfterEvent

        try:
            event = IfterEvent.query.get(event_id)
            return event.to_dict() if event else None
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}", exc_info=True)
            return None

    def create_event(self, event_data: Dict) -> Optional[Dict]:
        """Create a new iftar event"""
        from models import IfterEvent

        try:
            event = IfterEvent(
                mosque_id=event_data['mosque_id'],
                date=event_data['date'],
                start_time=event_data['start_time'],
                end_time=event_data.get('end_time'),
                location=event_data['location'],
                is_family_friendly=event_data.get('is_family_friendly', True),
                capacity=event_data.get('capacity'),
                is_recurring=event_data.get('is_recurring', False),
                recurrence_type=event_data.get('recurrence_type'),
                recurrence_end_date=event_data.get('recurrence_end_date')
            )

            self.db.session.add(event)
            self.db.session.commit()

            logger.info(f"Created new event for mosque {event.mosque_id} on {event.date}")
            return event.to_dict()

        except Exception as e:
            logger.error(f"Error creating event: {e}", exc_info=True)
            self.db.session.rollback()
            return None
import logging
from datetime import date, timedelta
import copy
from typing import List, Dict, Set, Optional

logger = logging.getLogger(__name__)

class IfterCalendar:
    """Handles all iftar event processing and calendar management"""

    def __init__(self, db):
        self.db = db
        self.processed_keys = set()  # For duplicate detection

    def generate_event_instances(self, event) -> List[dict]:
        """Generate all instances of a recurring event without duplicates"""
        if not event.is_recurring:
            return [self._create_event_instance(event, event.date)]

        instances = []
        start_date = event.date
        end_date = event.recurrence_end_date or (start_date + timedelta(days=30))  # Default 30 days

        # Determine recurrence pattern
        if event.recurrence_type == 'daily':
            delta = timedelta(days=1)
        elif event.recurrence_type == 'weekly':
            delta = timedelta(days=7)
        else:
            # Other recurrence patterns here
            return [self._create_event_instance(event, event.date)]

        # Generate unique instances
        current_date = start_date
        seen_dates = set()  # For duplicate detection

        while current_date <= end_date:
            if current_date not in seen_dates:
                seen_dates.add(current_date)

                # Create new instance with correct date
                instance = self._create_event_instance(event, current_date)
                instances.append(instance)

            current_date += delta

        return instances

    def get_events_for_period(self, start_date: date, end_date: date, 
                           mosque_id: Optional[int] = None,
                           family_only: bool = False,
                           event_type: str = 'all') -> List[dict]:
        """Get all events for a specific period with filtering"""
        from models import IfterEvent

        # Build base query with filters
        query = self.db.session.query(IfterEvent)

        if mosque_id:
            query = query.filter(IfterEvent.mosque_id == mosque_id)
        if family_only:
            query = query.filter(IfterEvent.is_family_friendly == True)
        if event_type != 'all':
            if event_type == 'daily':
                query = query.filter(IfterEvent.is_recurring == True,
                                   IfterEvent.recurrence_type == 'daily')
            elif event_type == 'weekly':
                query = query.filter(IfterEvent.is_recurring == True,
                                   IfterEvent.recurrence_type == 'weekly')
            elif event_type == 'single':
                query = query.filter(IfterEvent.is_recurring == False)

        # Get base events within period
        events = query.filter(
            (IfterEvent.date <= end_date) & 
            ((IfterEvent.recurrence_end_date >= start_date) | 
             (IfterEvent.recurrence_end_date.is_(None)))
        ).all()

        logger.debug(f"Found {len(events)} base events matching filters")

        # Generate all instances
        unique_events = {}  # Dictionary to prevent duplicates
        for event in events:
            instances = self.generate_event_instances(event)

            for instance in instances:
                instance_date = instance['date']

                # Only add if within range and not duplicate
                if start_date <= instance_date <= end_date:
                    key = f"{instance['id']}_{instance_date}_{instance['type']}"
                    if key not in unique_events:
                        unique_events[key] = instance

        # Sort events by date and time
        sorted_events = sorted(
            unique_events.values(), 
            key=lambda x: (x['date'], x['start_time'])
        )

        return sorted_events

    def _create_event_instance(self, event, instance_date: date) -> dict:
        """Create a standardized event instance"""
        return {
            'id': event.id,
            'type': 'single' if not event.is_recurring else event.recurrence_type,
            'mosque_id': event.mosque_id,
            'mosque_name': event.mosque.mosque_name if event.mosque else None,
            'date': instance_date,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'location': event.location,
            'is_family_friendly': event.is_family_friendly,
            'registration_required': event.registration_required,
            'capacity': event.capacity,
            'latitude': event.mosque.latitude if event.mosque else None,
            'longitude': event.mosque.longitude if event.mosque else None
        }
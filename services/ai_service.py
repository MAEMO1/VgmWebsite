import os
import logging
from anthropic import Anthropic
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY')
        )
        logger.info("AIService initialized with Anthropic client")

    def analyze_architecture_proposal(self, current_structure: dict) -> Optional[str]:
        """
        Analyze the proposal to separate the iftar functionality into a standalone app
        """
        try:
            prompt = f"""
            Please analyze this architectural proposal for a mosque management platform:

            Current Structure:
            {current_structure}

            The proposal is to separate the iftar calendar functionality into a standalone app.

            Please analyze considering:
            1. Modularity and maintainability
            2. Data sharing and integration challenges
            3. User experience impact
            4. Development complexity
            5. Performance implications
            6. Future scalability

            Focus specifically on:
            1. Whether separation would reduce current complexity
            2. How to handle shared data (users, mosques, prayer times)
            3. Integration options with the main platform
            4. Impact on the development process
            5. Effect on user navigation and experience

            Provide concrete recommendations on:
            1. Whether to proceed with separation
            2. If yes, what components should be separated
            3. How to maintain data consistency
            4. Best integration approach
            5. Migration strategy
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully received architecture analysis from Claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error analyzing architecture proposal: {e}")
            return None

    async def analyze_calendar_issue(self, calendar_data: dict) -> Optional[str]:
        """
        Analyze calendar data for duplicate events and other issues
        """
        try:
            prompt = f"""
            Please analyze this calendar data for issues:

            {calendar_data}

            Focus on:
            1. Identifying duplicate events
            2. Validating event recurrence logic
            3. Checking date range handling
            4. Verifying event type categorization

            Provide specific recommendations for:
            1. Fixing duplicate entries
            2. Improving recurrence handling
            3. Optimizing date range processing
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully received calendar analysis from Claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error analyzing calendar data: {e}")
            return None

    async def analyze_prayer_times(self, prayer_data: dict) -> Optional[str]:
        """
        Analyze prayer time data for consistency and variation
        """
        try:
            prompt = f"""
            Please analyze this prayer time data:

            {prayer_data}

            Focus on:
            1. Checking time variations between days
            2. Validating calculation methods
            3. Verifying timezone handling
            4. Analyzing source consistency

            Provide specific recommendations for:
            1. Ensuring proper time variations
            2. Improving API integration
            3. Handling multiple prayer time sources
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully received prayer time analysis from Claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error getting prayer times analysis: {e}")
            return None

    async def validate_calendar_logic(self, code_snippet: str) -> Optional[str]:
        """
        Validate calendar processing logic
        """
        try:
            prompt = f"""
            Please analyze this calendar processing code:

            {code_snippet}

            Focus on:
            1. Event recurrence handling
            2. Date range processing
            3. Duplicate prevention
            4. Data structure efficiency

            Provide specific recommendations for:
            1. Improving recurrence logic
            2. Optimizing data structures
            3. Preventing duplicate entries
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully received code analysis from Claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error validating calendar logic: {e}")
            return None

    def get_translation_feedback(self, source_text: str, translated_text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Get AI feedback on translation quality
        """
        try:
            prompt = f"""
            Please analyze this translation from {source_lang} to {target_lang}:

            Original ({source_lang}):
            {source_text}

            Translation ({target_lang}):
            {translated_text}

            Provide a brief assessment of:
            1. Accuracy of meaning
            2. Cultural appropriateness
            3. Religious terminology accuracy
            4. Suggested improvements
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully received translation feedback from Claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error getting translation feedback: {e}")
            return None

    def generate_event_description(self, event_type: str, title: str, target_lang: str) -> Optional[str]:
        """
        Generate culturally appropriate event descriptions
        """
        try:
            prompt = f"""
            Generate a culturally sensitive description in {target_lang} for this mosque event:

            Event Type: {event_type}
            Title: {title}

            Please ensure the description:
            1. Is respectful and appropriate for a mosque setting
            2. Uses correct Islamic terminology
            3. Is welcoming to all community members
            4. Includes any relevant cultural context
            5. Is concise but informative
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully generated event description")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating event description: {e}")
            return None

    def summarize_feedback(self, feedback_texts: list[str], target_lang: str) -> Optional[str]:
        """
        Summarize community feedback for mosque administrators
        """
        try:
            combined_feedback = "\n".join(feedback_texts)
            prompt = f"""
            Please analyze and summarize this mosque community feedback in {target_lang}:

            {combined_feedback}

            Provide a summary that includes:
            1. Key themes and patterns
            2. Main suggestions or concerns
            3. Positive feedback points
            4. Areas for improvement
            5. Priority recommendations
            """

            response = self.client.messages.create(
                model="claude-3.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully summarized community feedback")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error summarizing feedback: {e}")
            return None
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
                model="claude-3-5-sonnet-20241022",  # Using latest model
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
                model="claude-3-5-sonnet-20241022",  # Using latest model
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
                model="claude-3-5-sonnet-20241022",  # Using latest model
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            logger.info("Successfully summarized community feedback")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error summarizing feedback: {e}")
            return None

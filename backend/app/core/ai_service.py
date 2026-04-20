"""
AI Service using Google Cloud Vertex AI (Gemini).
Provides intelligent meetup recommendations with safe fallback handling.
"""

import vertexai
from vertexai.generative_models import GenerativeModel
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.model = None
        try:
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.location
            )
            self.model = GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            logger.warning(f"Vertex AI init failed: {e}")

    def _fallback(self):
        return {
            "title": "Board Games & Pizza",
            "location": "Dining Hall",
            "insight": "You might need a short break before diving back in."
        }

    def generate_meetup_match(self, interests, meetups):
        if not self.model:
            return self._fallback()

        prompt = f"""
        User intent: "{interests}"

        Meetups:
        {meetups}

        Choose the best match and respond ONLY in JSON:
        {{
            "title": "...",
            "location": "...",
            "insight": "..."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```", "")
            return json.loads(text)
        except Exception as e:
            logger.error(f"AI error: {e}")
            return self._fallback()


ai_engine = AIService()
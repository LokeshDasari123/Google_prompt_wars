import vertexai
from vertexai.generative_models import GenerativeModel
import logging
import json
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.model = None
        try:
            vertexai.init(project=settings.google_cloud_project, location=settings.location)
            self.model = GenerativeModel("gemini-2.5-flash")
            logger.info("Vertex AI initialized successfully with gemini-2.5-flash.")
        except Exception as e:
            logger.warning(f"Vertex AI initialization skipped: {e}")

    def generate_meetup_match(self, user_interests: str, meetup_descriptions: list[str]) -> dict:
        if not self.model:
            return {"title": "Fallback Event", "location": "Main Hall", "insight": "AI offline. Head to the main hall."}
            
        prompt = f"""
        You are 'Nexus', an elite matchmaking AI for a high-stakes tech conference.
        
        User's requested experience: "{user_interests}"
        
        Available active meetups: 
        {meetup_descriptions}
        
        INSTRUCTIONS:
        1. Analyze the user's underlying intent (are they looking to code, find money, relax, or socialize?).
        2. Evaluate every single active meetup against this intent.
        3. Select the ONE most perfect meetup.
        4. Write a highly personalized 1-sentence insight explaining exactly why this meetup aligns with their specific request.
        5. If the user's intent is complete gibberish, hostile, or completely unrelated to a physical event, recommend the "Board Games & Pizza" meetup and state that they need a break.
        
        CRITICAL: You MUST respond ONLY with a valid JSON object. Do not include markdown formatting or backticks.
        Format required:
        {{
            "title": "Exact Name of the Meetup",
            "location": "Suggested location extracted from description",
            "insight": "Your personalized 1-sentence explanation."
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"AI Generation Error: {str(e)}")
            return {"title": "System Overload", "location": "Networking Lounge", "insight": "Our AI is experiencing high traffic. Go mingle!"}

ai_engine = AIService()
import google.generativeai as genai
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    def __init__(self):
        self.text_model = genai.GenerativeModel("gemini-2.0-flash")
        self.json_model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def generate_text(self, prompt: str) -> str:
        response = await self.text_model.generate_content_async(prompt)
        return response.text

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def generate_json(self, prompt: str) -> dict:
        response = await self.json_model.generate_content_async(prompt)
        return json.loads(response.text)


gemini = GeminiService()

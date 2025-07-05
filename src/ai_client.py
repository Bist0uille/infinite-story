import os
import asyncio
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.critical("API key GEMINI_API_KEY not found in environment variables.")
            raise EnvironmentError("API key GEMINI_API_KEY not found in environment variables.")
        self.headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.model = "gemini-2.5-flash"
        logging.info(f"AIClient initialized with model: {self.model}")

    async def complete(self, messages: list[dict[str, str]]) -> str:
        # Convert messages to Gemini format
        contents = []
        for message in messages:
            # Map roles: system/user -> user, assistant -> model
            role = "user" if message.get("role") in ["system", "user"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 2048
            }
        }
        
        logging.debug(f"Sending request to AI. Data: {data}")

        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent", headers=self.headers, json=data, timeout=45) as response:
                        result = await response.json()
                        logging.debug(f"Response status: {response.status}")
                        logging.debug(f"Received raw response from AI: {result}")
                        
                        if response.status != 200:
                            logging.error(f"API Error: {result}")
                            raise Exception(f"API Error {response.status}: {result}")
                        
                        response_content = result['candidates'][0]['content']['parts'][0]['text']
                        logging.info("Successfully received and parsed AI response.")
                        return response_content
            except aiohttp.ClientError as e:
                logging.warning(f"AI request failed (attempt {attempt + 1}/{retries}): {e}")
                # Try to get response body for debugging
                try:
                    if hasattr(e, 'response') and e.response is not None:
                        error_text = await e.response.text()
                        logging.error(f"Error response body: {error_text}")
                except Exception:
                    pass
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    logging.error("AI request failed after all retries.", exc_info=True)
                    raise e
            except Exception as e:
                logging.error("An unexpected error occurred during AI request.", exc_info=True)
                raise e
        
        logging.critical("Failed to get a response from the AI after all retries.")
        raise Exception("Failed to get a response from the AI after several retries.")

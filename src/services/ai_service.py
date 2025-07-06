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

    def _extract_response_content(self, result):
        """
        Extraction robuste du contenu de réponse avec gestion des cas d'erreur
        """
        try:
            # Vérifier la structure de base
            if "candidates" not in result or not result["candidates"]:
                logging.error("No candidates in response")
                return None, "NO_CANDIDATES"
            
            candidate = result["candidates"][0]
            
            # Vérifier finishReason pour détecter les blocages
            finish_reason = candidate.get("finishReason")
            if finish_reason and finish_reason != "STOP":
                logging.warning(f"Response blocked. Finish reason: {finish_reason}")
                return None, finish_reason
            
            # Vérifier la présence de content
            if "content" not in candidate:
                logging.error("No content in candidate")
                return None, "NO_CONTENT"
            
            content = candidate["content"]
            
            # Vérifier la présence de parts
            if "parts" not in content or not content["parts"]:
                logging.error("No parts in content")
                return None, "NO_PARTS"
            
            # Extraire le texte
            parts = content["parts"]
            if "text" not in parts[0]:
                logging.error("No text in first part")
                return None, "NO_TEXT"
            
            return parts[0]["text"], "SUCCESS"
            
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Error extracting response content: {e}")
            logging.debug(f"Response structure: {result}")
            return None, f"EXTRACTION_ERROR: {str(e)}"

    async def complete(self, messages: list[dict[str, str]]) -> str:
        # Contexte plus large avec gemini-2.5-flash
        if len(messages) > 20:  # Beaucoup plus de contexte autorisé
            # Garder le système + les 18 derniers
            messages = [messages[0]] + messages[-18:]
            logging.info(f"Context truncated to {len(messages)} messages")
        # Convert messages to Gemini format
        contents = []
        for message in messages:
            # Map roles: system/user -> user, assistant -> model
            role = "user" if message.get("role") in ["system", "user"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })
        
        # Configuration avec safety settings plus permissifs pour les RPG
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 8192
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
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
                        
                        # Extraction robuste avec gestion d'erreurs
                        response_content, status = self._extract_response_content(result)
                        
                        if response_content is not None:
                            logging.info("Successfully received and parsed AI response.")
                            return response_content
                        else:
                            # Gestion des différents types d'erreurs
                            if status == "SAFETY":
                                error_msg = "Contenu bloqué par les filtres de sécurité. Tentative avec un prompt modifié..."
                                logging.warning(error_msg)
                                if attempt < retries - 1:
                                    # Réessayer avec un prompt plus neutre
                                    await asyncio.sleep(2)
                                    continue
                                else:
                                    raise Exception("Contenu systématiquement bloqué par les filtres de sécurité après plusieurs tentatives.")
                            
                            elif status in ["NO_CANDIDATES", "NO_CONTENT", "NO_PARTS", "NO_TEXT"]:
                                error_msg = f"Structure de réponse invalide: {status}"
                                logging.error(error_msg)
                                if attempt < retries - 1:
                                    await asyncio.sleep(1)
                                    continue
                                else:
                                    raise Exception(f"Structure de réponse invalide: {status}")
                            
                            else:
                                error_msg = f"Erreur d'extraction inconnue: {status}"
                                logging.error(error_msg)
                                if attempt < retries - 1:
                                    await asyncio.sleep(1)
                                    continue
                                else:
                                    raise Exception(f"Erreur d'extraction: {status}")
                        
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
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise e
        
        logging.critical("Failed to get a response from the AI after all retries.")
        raise Exception("Failed to get a response from the AI after several retries.")
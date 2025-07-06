"""
AI Service for RPBOT_v5.1

Handles communication with Gemini API and integrates WorldState information
for enhanced narrative generation.
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime
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
        
        # Token tracking for session analytics
        self.session_stats = {
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "thoughts_tokens": 0,
            "calls_by_purpose": {},
            "session_start": None
        }
        
        logging.info(f"AIClient initialized with model: {self.model}")

    def start_session(self):
        """Initialize session tracking."""
        self.session_stats["session_start"] = datetime.now()
        logging.info("AI session tracking started.")

    def _track_token_usage(self, result, purpose="general"):
        """Extract and track token usage from API response."""
        try:
            if "usageMetadata" in result:
                metadata = result["usageMetadata"]
                
                input_tokens = metadata.get("promptTokenCount", 0)
                output_tokens = metadata.get("candidatesTokenCount", 0)
                total_tokens = metadata.get("totalTokenCount", 0)
                thoughts_tokens = metadata.get("thoughtsTokenCount", 0)
                
                # Update session stats
                self.session_stats["total_calls"] += 1
                self.session_stats["total_input_tokens"] += input_tokens
                self.session_stats["total_output_tokens"] += output_tokens
                self.session_stats["total_tokens"] += total_tokens
                self.session_stats["thoughts_tokens"] += thoughts_tokens
                
                # Track by purpose
                if purpose not in self.session_stats["calls_by_purpose"]:
                    self.session_stats["calls_by_purpose"][purpose] = {
                        "calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0
                    }
                
                self.session_stats["calls_by_purpose"][purpose]["calls"] += 1
                self.session_stats["calls_by_purpose"][purpose]["input_tokens"] += input_tokens
                self.session_stats["calls_by_purpose"][purpose]["output_tokens"] += output_tokens
                self.session_stats["calls_by_purpose"][purpose]["total_tokens"] += total_tokens
                
                logging.debug(f"Token usage tracked - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}, Thoughts: {thoughts_tokens}")
                
        except Exception as e:
            logging.warning(f"Failed to track token usage: {e}")

    def get_session_summary(self):
        """Get a formatted summary of the session's token usage."""
        if not self.session_stats["session_start"]:
            return "No session data available."
        
        duration = datetime.now() - self.session_stats["session_start"]
        
        summary = []
        summary.append("=" * 60)
        summary.append("🎯 SESSION TOKEN USAGE SUMMARY")
        summary.append("=" * 60)
        summary.append(f"📅 Session Duration: {duration}")
        summary.append(f"🔢 Total API Calls: {self.session_stats['total_calls']}")
        summary.append(f"📥 Total Input Tokens: {self.session_stats['total_input_tokens']:,}")
        summary.append(f"📤 Total Output Tokens: {self.session_stats['total_output_tokens']:,}")
        summary.append(f"🧠 Thoughts Tokens: {self.session_stats['thoughts_tokens']:,}")
        summary.append(f"💯 TOTAL TOKENS: {self.session_stats['total_tokens']:,}")
        summary.append("")
        
        # Breakdown by purpose
        if self.session_stats["calls_by_purpose"]:
            summary.append("📊 Breakdown by Purpose:")
            summary.append("-" * 40)
            for purpose, stats in self.session_stats["calls_by_purpose"].items():
                summary.append(f"  {purpose.upper()}:")
                summary.append(f"    Calls: {stats['calls']}")
                summary.append(f"    Input: {stats['input_tokens']:,} tokens")
                summary.append(f"    Output: {stats['output_tokens']:,} tokens")
                summary.append(f"    Total: {stats['total_tokens']:,} tokens")
                summary.append("")
        
        # Cost estimation (approximate)
        input_cost = self.session_stats['total_input_tokens'] * 0.000125 / 1000  # $0.125 per 1M tokens
        output_cost = self.session_stats['total_output_tokens'] * 0.000375 / 1000  # $0.375 per 1M tokens
        total_cost = input_cost + output_cost
        
        summary.append("💰 Estimated Cost (Gemini 2.5-flash):")
        summary.append(f"    Input: ${input_cost:.4f}")
        summary.append(f"    Output: ${output_cost:.4f}")
        summary.append(f"    TOTAL: ${total_cost:.4f}")
        summary.append("=" * 60)
        
        return "\n".join(summary)

    def log_session_summary(self):
        """Log the session summary to the logging system."""
        summary = self.get_session_summary()
        logging.info(f"\n{summary}")

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

    def _format_world_context(self, world_state):
        """
        Format WorldState information for AI context.
        Creates a structured summary that helps the AI maintain consistency.
        """
        if not world_state:
            return ""
        
        context_parts = []
        
        # Hero information
        hero = world_state.characters.get("main_character")
        if hero:
            hero_info = f"Héros: {hero.name} ({hero.status})"
            if hero.traits:
                hero_info += f", traits: {', '.join(hero.traits)}"
            context_parts.append(hero_info)
        
        # Current location
        if hero and hero.location_id:
            location = world_state.locations.get(hero.location_id)
            if location:
                loc_info = f"Lieu actuel: {location.name}"
                if location.description:
                    loc_info += f" - {location.description}"
                context_parts.append(loc_info)
        
        # Known characters (NPCs)
        npcs = [char for char_id, char in world_state.characters.items() 
                if char_id != "main_character"]
        if npcs:
            npc_names = [f"{char.name} ({char.status})" for char in npcs]
            context_parts.append(f"PNJ connus: {', '.join(npc_names)}")
        
        # Inventory
        if world_state.inventory:
            items = ', '.join(sorted(world_state.inventory))
            context_parts.append(f"Inventaire: {items}")
        
        # Active flags
        active_flags = [flag for flag, value in world_state.flags.items() if value]
        if active_flags:
            context_parts.append(f"États actifs: {', '.join(active_flags)}")
        
        # Recent events context
        recent_events = world_state.get_recent_events(3)
        if recent_events:
            event_summaries = [event.descr[:50] + "..." if len(event.descr) > 50 else event.descr 
                             for event in recent_events]
            context_parts.append(f"Événements récents: {'; '.join(event_summaries)}")
        
        return " | ".join(context_parts) if context_parts else ""

    async def complete(self, messages: list[dict[str, str]], world_state=None, purpose="story_generation") -> str:
        """
        Enhanced complete method that integrates WorldState context.
        
        Args:
            messages: List of conversation messages
            world_state: Optional WorldState for context enhancement
        """
        # Contexte plus large avec gemini-2.5-flash
        if len(messages) > 20:  # Beaucoup plus de contexte autorisé
            # Garder le système + les 18 derniers
            messages = [messages[0]] + messages[-18:]
            logging.info(f"Context truncated to {len(messages)} messages")
        
        # Convert messages to Gemini format
        contents = []
        for i, message in enumerate(messages):
            # Map roles: system/user -> user, assistant -> model
            role = "user" if message.get("role") in ["system", "user"] else "model"
            
            # Enhance system message with world context
            content_text = message["content"]
            if i == 0 and message.get("role") == "system" and world_state:
                world_context = self._format_world_context(world_state)
                if world_context:
                    content_text += f"\n\nCONTEXTE ACTUEL: {world_context}"
                    logging.debug(f"Enhanced system message with world context: {world_context}")
            
            contents.append({
                "role": role,
                "parts": [{"text": content_text}]
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
        
        logging.debug(f"Sending request to AI. Messages: {len(messages)}")
        if world_state:
            logging.debug(f"WorldState context included: {len(world_state.characters)} chars, {len(world_state.locations)} locs")

        retries = 3
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent", headers=self.headers, json=data, timeout=45) as response:
                        result = await response.json()
                        logging.debug(f"Response status: {response.status}")
                        
                        if response.status != 200:
                            logging.error(f"API Error: {result}")
                            raise Exception(f"API Error {response.status}: {result}")
                        
                        # Track token usage
                        self._track_token_usage(result, purpose)
                        
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

    async def complete_with_context(self, messages: list[dict[str, str]], world_state, purpose: str = "story_generation") -> str:
        """
        Wrapper method for backward compatibility and specific purposes.
        """
        return await self.complete(messages, world_state)
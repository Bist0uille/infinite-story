import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any

from models.world_state import WorldState, Character, Location, Event
from services.migration_service import MigrationService
from services.ai_service import AIClient 

class GameEngine:
    """Core game engine handling story state and game logic using WorldState."""

    def __init__(self, ai_client: AIClient):
        self.world_state: WorldState = WorldState()
        self.hero_name: str = "Tim"
        self.debug_mode: bool = True
        self.migration_service = MigrationService()
        self.ai_client = ai_client
        logging.info("GameEngine initialized with AIClient.")

    async def _extract_entities_from_narrative(self, narrative: str) -> Dict[str, Any]:
        """Uses AI to extract characters, locations, and hero status from a narrative text."""
        if not narrative.strip():
            return {}

        prompt = (
            "Analyse le texte suivant. Extrais les personnages (PNJ), les lieux, et le nouveau statut du joueur. "
            "Ignore le personnage principal du joueur dans la liste des PNJ. "
            "Retourne le résultat dans un format JSON strict avec les clés 'characters' (liste de {'name', 'description'}), "
            "'locations' (liste de {'name', 'description'}), et 'hero_status' (string).\n"
            f"Texte à analyser:\n---\n{narrative}\n---\n\n"
            "JSON:"
        )
        
        response = ""
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.ai_client.complete(messages, None, "entity_extraction")
            json_response = response.strip().replace("```json", "").replace("```", "")
            entities = json.loads(json_response)
            logging.info(f"Successfully extracted entities: {entities}")
            return entities
        except Exception as e:
            logging.error(f"Entity extraction failed: {e}. Response: {response}", exc_info=True)
            return {}

    async def update_world_state_from_narrative(self, narrative: str):
        """Extracts entities from narrative and updates the world state."""
        entities = await self._extract_entities_from_narrative(narrative)
        
        hero = self.world_state.characters.get("main_character")
        current_location_id = hero.location_id if hero else "unknown_location"

        if hero and entities.get("hero_status"):
            hero.status = entities["hero_status"]
            logging.info(f"Hero status updated to: {hero.status}")

        for char_data in entities.get("characters", []):
            char_name = char_data.get("name")
            if char_name and char_name.lower() != self.hero_name.lower():
                if not any(c.name.lower() == char_name.lower() for c in self.world_state.characters.values()):
                    new_char = Character(
                        id=f"char_{char_name.lower().replace(' ', '_')}",
                        name=char_name,
                        traits=[char_data.get("description", "Inconnu")],
                        location_id=current_location_id,
                        status="alive"
                    )
                    self.world_state.add_character(new_char)

        for loc_data in entities.get("locations", []):
            loc_name = loc_data.get("name")
            if loc_name:
                if not any(l.name.lower() == loc_name.lower() for l in self.world_state.locations.values()):
                    new_loc = Location(
                        id=f"loc_{loc_name.lower().replace(' ', '_')}",
                        name=loc_name,
                        description=loc_data.get("description", "Lieu mystérieux")
                    )
                    self.world_state.add_location(new_loc)
                    if hero: hero.location_id = new_loc.id

    def clear_game_state(self):
        self.world_state = WorldState()

    def set_hero_name(self, name: str):
        self.hero_name = name.strip() or "Aventurier"
        if "main_character" not in self.world_state.characters:
            self.world_state = self.migration_service.create_empty_world_state(self.hero_name)
        else:
            self.world_state.characters["main_character"].name = self.hero_name

    def add_system_message(self, content: str):
        event = Event(id=f"system_{len(self.world_state.timeline)}", descr=content, ts=self.get_current_turn_number(), impact={"type": "system_message"})
        self.world_state.add_event(event)

    def add_user_message(self, content: str):
        event = Event(id=f"user_{len(self.world_state.timeline)}", descr=content, ts=self.get_current_turn_number(), impact={"type": "user_choice"})
        self.world_state.add_event(event)

    def add_assistant_message(self, content: str):
        narrative, _ = self.extract_choices(content)
        event = Event(id=f"assistant_{len(self.world_state.timeline)}", descr=narrative, ts=self.get_current_turn_number(), impact={"type": "assistant_response"}, raw_response=content)
        self.world_state.add_event(event)

    def build_system_prompt(self, base_prompt: str, style_instruction: str) -> str:
        world_summary = self.world_state.get_world_summary(exclude_defaults=True)
        context = f"Contexte: {world_summary}. " if world_summary else ""
        universe_type = "adventure"
        if any(w in base_prompt.lower() for w in ["fantasy", "médiéval"]): universe_type = "fantasy"
        elif any(w in base_prompt.lower() for w in ["science", "spatial"]): universe_type = "scifi"
        templates = {"fantasy": f"Aventure fantasy avec {self.hero_name}.", "scifi": f"Aventure spatiale avec {self.hero_name}.", "adventure": f"Aventure avec {self.hero_name}."}
        style = self._compact_style(style_instruction)
        return f"{templates[universe_type]} {style} {context}Format strict: histoire courte + 4 choix numérotés."
    
    def _compact_style(self, style: str) -> str:
        s = style.lower()
        if "dramatique" in s: return "Style: tension."
        if "humoristique" in s: return "Style: léger."
        if "poétique" in s: return "Style: évocateur."
        return "Style: direct."

    def build_prompt_with_context(self, user_input: str, is_continuation: bool = False, previous_response: Optional[str] = None) -> str:
        context_summary = self.world_state.get_world_summary(exclude_defaults=True)
        context = f"Contexte: {context_summary}. " if context_summary else ""
        if previous_response: return "Corrige ta réponse. Histoire + 4 choix."
        if is_continuation: return f"Continue. {context}Histoire + 4 choix."
        return f"Choix: '{user_input}'. {context}Continue. Histoire + 4 choix."

    def extract_choices(self, text: str) -> Tuple[str, List[str]]:
        lines = text.replace("{hero_name}", self.hero_name).strip().split("\n")
        choices, narrative = [], []
        for line in lines:
            if re.match(r"^\s*(\d+[.\)]|[-*])\s", line):
                choices.append(re.sub(r"^\s*(\d+[.\)]|[-*])\s*", "", line).strip())
            else:
                narrative.append(line)
        if not choices and len(narrative) > 4:
            choices = narrative[-4:]
            narrative = narrative[:-4]
        return "\n".join(narrative).strip(), choices

    def load_game_state(self, save_data: Dict[str, Any]):
        try:
            self.world_state = WorldState.model_validate(save_data)
            self.hero_name = self.world_state.characters.get("main_character").name
        except Exception:
            self.world_state = self.migration_service.migrate_from_save_file(save_data)
            self.hero_name = self.world_state.characters.get("main_character").name

    def get_save_data(self) -> Dict[str, Any]:
        return self.world_state.model_dump()

    def get_last_narrative_and_choices(self) -> Tuple[str, List[str]]:
        for event in reversed(self.world_state.timeline):
            if event.impact.get("type") == "assistant_response" and event.raw_response:
                return self.extract_choices(event.raw_response)
        return "", []

    def get_current_turn_number(self) -> int:
        return sum(1 for e in self.world_state.timeline if e.impact.get("type") == "assistant_response")

    def is_game_started(self) -> bool:
        return len(self.world_state.timeline) > 1
        
    def get_story_log_for_api(self) -> List[Dict[str, str]]:
        log = []
        relevant_events = self.world_state.timeline[-6:]
        if self.world_state.timeline and self.world_state.timeline[0] not in relevant_events:
            relevant_events.insert(0, self.world_state.timeline[0])
        for event in relevant_events:
            role = event.impact.get("type", "unknown").split('_')[0]
            if role in ["system", "user", "assistant"]:
                content = event.raw_response if role == "assistant" and event.raw_response else event.descr
                log.append({"role": role, "content": content})
        return log

    def get_full_story_text(self) -> str:
        return "\n\n".join(f"> {e.descr}" if e.impact.get("type") == "user_choice" else e.descr for e in self.world_state.timeline if e.impact.get("type") in ["assistant_response", "user_choice"])
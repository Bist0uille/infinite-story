"""
Game engine core - pure game logic without UI dependencies
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Any


class GameEngine:
    """Core game engine handling story state and game logic"""
    
    def __init__(self):
        self.story_log: List[Dict[str, str]] = []
        self.world_state: Dict[str, str] = {}
        self.hero_name: str = "Tim"
        self.debug_mode: bool = True
        
    def clear_game_state(self):
        """Reset game state for new game"""
        self.story_log.clear()
        self.world_state.clear()
        
    def set_hero_name(self, name: str):
        """Set the hero's name"""
        self.hero_name = name.strip() or "Aventurier"
        
    def add_system_message(self, content: str):
        """Add system message to story log"""
        self.story_log.append({"role": "system", "content": content})
        
    def add_user_message(self, content: str):
        """Add user message to story log"""
        self.story_log.append({"role": "user", "content": content})
        
    def add_assistant_message(self, content: str):
        """Add assistant message to story log"""
        self.story_log.append({"role": "assistant", "content": content})
        
    def remove_last_message(self):
        """Remove the last message from story log"""
        if self.story_log:
            self.story_log.pop()
            
    def build_system_prompt(self, base_prompt: str, style_instruction: str) -> str:
        """Build adaptive system prompt based on game phase"""
        
        # Détecter le type d'univers de façon intelligente
        if any(word in base_prompt.lower() for word in ["fantasy", "médiéval", "dragon", "magie"]):
            universe_type = "fantasy"
        elif any(word in base_prompt.lower() for word in ["science", "spatial", "vaisseau", "captain"]):
            universe_type = "scifi"
        else:
            universe_type = "adventure"
        
        # Templates adaptatifs ultra-compacts
        universe_templates = {
            "fantasy": f"Aventure fantasy avec {self.hero_name} dans un monde médiéval.",
            "scifi": f"Aventure spatiale avec le capitaine {self.hero_name}.",
            "adventure": f"Aventure avec {self.hero_name}."
        }
        
        # Style compacté
        style_compact = self._compact_style(style_instruction)
        
        # Prompt final très compact mais informatif
        return f"{universe_templates[universe_type]} {style_compact} Format strict: histoire courte + 4 choix numérotés."
    
    def _compact_style(self, style_instruction: str) -> str:
        """Compact style instruction to essential keywords"""
        style = style_instruction.lower()
        
        if "dramatique" in style or "suspense" in style:
            return "Style: tension et suspense."
        elif "humoristique" in style or "amusant" in style:
            return "Style: léger et drôle."
        elif "poétique" in style or "imagé" in style:
            return "Style: riche et évocateur."
        else:
            return "Style: direct et clair."
        
    def build_prompt_with_context(self, user_input: str, is_continuation: bool = False, previous_response: Optional[str] = None) -> str:
        """Build context-aware prompt without world state (temporarily disabled)"""
        
        # Construire un contexte à partir des derniers messages
        context_summary = self._build_recent_context()
        
        if previous_response:
            prompt = f"Corrige ta réponse précédente. Histoire + 4 choix numérotés."
        elif is_continuation:
            prompt = f"Continue l'aventure. {context_summary} Histoire + 4 choix."
        else:
            # Version adaptative selon la longueur de l'histoire
            if len(self.story_log) <= 2:  # Début d'aventure
                prompt = f"Choix du joueur: '{user_input}'. Commence l'aventure avec ce choix. Histoire + 4 choix."
            else:  # Continuation
                prompt = f"Choix: '{user_input}'. {context_summary} Continue l'histoire + 4 choix."
        
        return prompt
    
    def _build_recent_context(self) -> str:
        """Build compact context from recent messages"""
        if len(self.story_log) <= 2:
            return ""
        
        # Prendre les 2 derniers messages assistant (les dernières histoires)
        recent_assistant_messages = [
            msg for msg in self.story_log[-4:] 
            if msg.get('role') == 'assistant'
        ]
        
        if not recent_assistant_messages:
            return ""
        
        # Extraire juste le début de la dernière histoire pour contexte
        last_story = recent_assistant_messages[-1]['content']
        story_start = last_story.split('\n')[0]  # Première ligne seulement
        
        if len(story_start) > 100:
            story_start = story_start[:100] + "..."
        
        return f"Contexte récent: {story_start}"
        
    def extract_choices(self, text: str) -> Tuple[str, List[str]]:
        """Extract narrative and choices from AI response"""
        text = text.replace("{hero_name}", self.hero_name)
        lines = text.strip().split("\n")
        choices, narrative = [], []
        
        for line in lines:
            if re.match(r"^\s*(\d+[\.\)]|[-*])\s", line):
                choices.append(re.sub(r"^\s*(\d+[\.\)]|[-*])\s*", "", line).strip())
            else:
                narrative.append(line)
                
        if not choices and len(narrative) > 4:
            choices = narrative[-4:]
            narrative = narrative[:-4]
            logging.warning("Used fallback choice extraction logic.")
            
        logging.debug(f"Extracted {len(choices)} choices and narrative part.")
        return "\n".join(narrative).strip(), choices
        
    def update_world_state_from_facts(self, raw_facts: str):
        """Update world state from extracted facts"""
        for line in raw_facts.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    self.world_state[key] = value
                    logging.info(f"Updated world state: {key} = {value}")
                    
    def load_game_state(self, save_data: Dict[str, Any]):
        """Load game state from save data"""
        self.story_log = save_data.get("story_log", [])
        self.world_state = save_data.get("world_state", {})
        
    def get_save_data(self) -> Dict[str, Any]:
        """Get current game state for saving"""
        return {
            "story_log": self.story_log,
            "world_state": self.world_state
        }
        
    def get_last_narrative_and_choices(self) -> Tuple[str, List[str]]:
        """Get narrative and choices from last assistant message"""
        if self.story_log and self.story_log[-1]["role"] == "assistant":
            return self.extract_choices(self.story_log[-1]["content"])
        return "", []
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
        """Build the complete system prompt for game start"""
        prompt_system = f"{base_prompt}\n\n"
        
        has_custom_instructions = "instructions pour l'ia" in base_prompt.lower() or \
                                  "style narratif" in base_prompt.lower() or \
                                  "instructions pour l'ia" in style_instruction.lower()
        
        if not has_custom_instructions:
            prompt_system += (
                "**Instructions strictes pour le Maître du Jeu (IA) :**\n"
                f"1.  **Style Narratif :** {style_instruction}\n"
                "2.  **Format de réponse :** Ta réponse doit TOUJOURS être une partie narrative suivie d'une liste de 4 choix numérotés (1. à 4.).\n"
                "3.  **Continuité :** L'histoire doit être cohérente avec les choix précédents et les faits établis.\n"
                "4.  **Ne jamais conclure :** L'aventure ne doit jamais se terminer. Propose toujours des choix pour continuer.\n"
                f"5.  **Héros :** Le personnage principal est et restera {self.hero_name}."
            )
        else:
            if style_instruction not in base_prompt:
                prompt_system += f"**Style Narratif Additionnel :** {style_instruction}\n\n"
            prompt_system += (
                "**Règles de base du jeu :**\n"
                "- Ta réponse doit TOUJOURS être une partie narrative suivie d'une liste de 4 choix numérotés (1. à 4.).\n"
                "- L'aventure ne doit jamais se terminer.\n"
                f"- Le personnage principal est et restera {self.hero_name}.\n"
                "- Maintiens une continuité stricte avec les faits établis dans la section 'FAITS ÉTABLIS'."
            )
        
        return prompt_system
        
    def build_prompt_with_world_state(self, user_input: str, is_continuation: bool = False, previous_response: Optional[str] = None) -> str:
        """Build prompt including world state context"""
        if previous_response:
            prompt = f"Ta réponse précédente était invalide : '{previous_response}'. Corrige-la. Fournis une narration et 4 choix numérotés."
        elif is_continuation:
            prompt = "Continue l'histoire et propose 4 nouveaux choix."
        else:
            prompt = f"Le joueur choisit : '{user_input}'. Décris les conséquences et propose 4 nouveaux choix."
            
        if not self.world_state:
            return prompt
            
        state_summary = "\n\n**FAITS ÉTABLIS (à respecter impérativement) :**\n"
        for key, value in self.world_state.items():
            state_summary += f"- {key}: {value}\n"
            
        return state_summary + "\n" + prompt
        
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
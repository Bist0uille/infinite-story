import os
import json
import logging

# --- Constants ---
SAVE_DIR = "saves"
CUSTOM_UNIVERSES_FILE = "custom_universes.json"
PRESET_UNIVERSES_FILE = "preset_universes.json"
PRESET_STYLES_FILE = "preset_styles.json"
CUSTOM_STYLES_FILE = "custom_styles.json"

# --- Utility Functions ---
def load_json(file_path, default_data=None):
    """Loads a JSON file and returns its content."""
    if default_data is None:
        default_data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logging.info(f"Successfully loaded JSON from {file_path}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading {file_path}: {e}", exc_info=True)
            return default_data
    logging.warning(f"File not found: {file_path}. Returning default data.")
    return default_data

def save_json(file_path, data):
    """Saves data to a JSON file."""
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"Successfully saved JSON to {file_path}")
    except IOError as e:
        logging.error(f"Error saving to {file_path}: {e}", exc_info=True)

def init_default_files():
    """Creates default JSON configuration files if they don't exist."""
    if not os.path.exists(PRESET_UNIVERSES_FILE):
        logging.info(f"{PRESET_UNIVERSES_FILE} not found, creating default.")
        default_universes = {
            "Fantasy Classique": {
                "prompt": "Le héros, {hero_name}, est un aventurier dans un royaume médiéval fantastique. Il se trouve dans un endroit aléatoire - que ce soit une forêt mystérieuse, une route de montagne, une cité marchande, des ruines anciennes, ou tout autre lieu que tu inventeras. Ce monde n'est pas aussi simple qu'il y paraît - les habitants cachent des secrets, les nobles ont des agendas politiques, et même les quêtes les plus simples ont des conséquences inattendues.\n\n**Instructions pour l'IA :**\n- Propose toujours des choix avec des dilemmes moraux\n- Les PNJ ont leurs propres motivations et ne sont pas toujours honnêtes\n- Inclus un choix créatif ou inattendu dans chaque situation\n- Les actions ont des conséquences qui reviennent plus tard\n- Évite les solutions parfaites - tout a un prix"
            },
            "Science-Fiction Spatiale": {
                "prompt": "Le capitaine {hero_name} se trouve dans une situation spatiale aléatoire - que ce soit sur une station spatiale, une planète inconnue, dans l'espace intersidéral, ou dans une situation d'urgence que tu inventeras. Les défis technologiques et les tensions politiques compliquent chaque décision.\n\n**Instructions pour l'IA :**\n- Chaque décision a des répercussions sur l'équipage et la mission\n- Les membres d'équipage ont leurs propres agendas\n- Inclus des choix technologiques créatifs\n- Les conséquences des décisions précédentes affectent les situations futures\n- Évite les solutions parfaites - l'espace est dangereux"
            }
        }
        save_json(PRESET_UNIVERSES_FILE, default_universes)

    if not os.path.exists(PRESET_STYLES_FILE):
        logging.info(f"{PRESET_STYLES_FILE} not found, creating default.")
        default_styles = {
            "Classique": "Raconte l'histoire de manière directe et factuelle.",
            "Poétique": "Utilise un langage riche et imagé, avec des métaphores et des descriptions évocatrices pour raconter l'histoire.",
            "Humoristique": "Adopte un ton léger et amusant. N'hésite pas à inclure des situations comiques ou des dialogues pleins d'esprit.",
            "Dramatique": "Crée de la tension et du suspense. Utilise des descriptions intenses, des dialogues chargés d'émotion et des rebondissements inattendus. Chaque choix doit sembler crucial."
        }
        save_json(PRESET_STYLES_FILE, default_styles)
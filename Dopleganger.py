import os
import json
import customtkinter as ctk
from tkinter import StringVar, simpledialog
from dotenv import load_dotenv
import asyncio
import aiohttp
import re
import traceback

# --- Constants ---
SAVE_DIR = "saves"
CUSTOM_UNIVERSES_FILE = "custom_universes.json"
PRESET_UNIVERSES_FILE = "preset_universes.json"
NARRATIVE_STYLES_FILE = "narrative_styles.json"
CUSTOM_STYLES_FILE = "custom_styles.json"

# --- Utility Functions ---
def _load_json_file(file_path, default_data=None):
    if default_data is None:
        default_data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_data
    return default_data

def _save_json_file(file_path, data):
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def initialize_default_files():
    """Creates default JSON configuration files if they don't exist."""
    if not os.path.exists(PRESET_UNIVERSES_FILE):
        default_universes = {
            "Fantasy Classique": {
                "prompt": "Le héros, {hero_name}, est un jeune aventurier dans un royaume médiéval fantastique. Il commence son voyage dans le village de Chêneval, cherchant la gloire et la fortune. Sa première quête l'attend à l'auberge locale."
            },
            "Science-Fiction Spatiale": {
                "prompt": "Le capitaine {hero_name} est aux commandes du vaisseau d'exploration 'L'Errant des Étoiles'. Une anomalie spatiale inconnue vient d'apparaître sur les capteurs, droit devant. L'équipage attend ses ordres."
            }
        }
        _save_json_file(PRESET_UNIVERSES_FILE, default_universes)

    if not os.path.exists(NARRATIVE_STYLES_FILE):
        default_styles = {
            "Classique": "Raconte l'histoire de manière directe et factuelle.",
            "Poétique": "Utilise un langage riche et imagé, avec des métaphores et des descriptions évocatrices pour raconter l'histoire.",
            "Humoristique": "Adopte un ton léger et amusant. N'hésite pas à inclure des situations comiques ou des dialogues pleins d'esprit."
        }
        _save_json_file(NARRATIVE_STYLES_FILE, default_styles)

# --- API Configuration ---
load_dotenv()
AI4CHAT_API_KEY = os.getenv("AI4CHAT_API_KEY")
if not AI4CHAT_API_KEY:
    raise EnvironmentError("Clé API AI4Chat manquante dans le fichier .env")

HEADERS = {
    "Authorization": AI4CHAT_API_KEY,
    "Content-Type": "application/json"
}

# --- Main Application Classes ---
class AsyncioTk(ctk.CTk):
    """A CustomTkinter root window with an integrated asyncio event loop."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.running = True
        self.loop = asyncio.get_event_loop()

    def on_closing(self):
        self.running = False

    async def run(self):
        while self.running:
            self.update()
            await asyncio.sleep(0.01)

class RPGApp(AsyncioTk):
    """The main application class for the RPG adventure game."""
    def __init__(self):
        super().__init__()

        self.title("RPBot IA - Aventure Ultime (Doppelganger Edition)")
        self.geometry("1200x750")
        ctk.set_appearance_mode("Dark")

        # --- Game State ---
        self.story_log = []
        self.debug_mode = True
        self.hero_name = "Tim"
        self.font_size = 14

        # --- Data Loading ---
        initialize_default_files()
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
            
        self.preset_universes = _load_json_file(PRESET_UNIVERSES_FILE)
        self.custom_universes = _load_json_file(CUSTOM_UNIVERSES_FILE)
        self.preset_styles = _load_json_file(NARRATIVE_STYLES_FILE)
        self.custom_styles = _load_json_file(CUSTOM_STYLES_FILE)
        
        self.all_universes = {**self.preset_universes, **self.custom_universes}
        self.all_styles = {**self.preset_styles, **self.custom_styles}

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.text = ctk.CTkTextbox(main_frame, state="disabled", wrap="word", font=("Arial", self.font_size))
        self.text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.text.bind("<Control-MouseWheel>", self._on_mouse_wheel)
        self.text.bind("<Command-MouseWheel>", self._on_mouse_wheel)

        self.choices_frame = ctk.CTkScrollableFrame(main_frame, label_text="Vos Choix")
        self.choices_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        control_panel = ctk.CTkFrame(self)
        control_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        control_panel.grid_rowconfigure(0, weight=1)
        control_panel.grid_columnconfigure(0, weight=1)

        tab_view = ctk.CTkTabview(control_panel, anchor="w")
        tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self._create_play_tab(tab_view.add("▶ Jouer"))
        self._create_universes_tab(tab_view.add("🌌 Univers"))
        self._create_styles_tab(tab_view.add("🎨 Styles"))
        self._create_saves_tab(tab_view.add("💾 Sauvegardes"))

    def _create_play_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        char_frame = ctk.CTkFrame(tab)
        char_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(char_frame, text="Personnage", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        self.hero_name_entry = ctk.CTkEntry(char_frame, placeholder_text="Nom du héros")
        self.hero_name_entry.pack(pady=5, padx=10, fill="x")
        self.hero_name_entry.insert(0, self.hero_name)

        uni_frame = ctk.CTkFrame(tab)
        uni_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(uni_frame, text="Univers & Style", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        
        ctk.CTkLabel(uni_frame, text="Choix de l'univers :").pack(pady=(5,0))
        self.story_type_var = StringVar(value=list(self.all_universes.keys())[0] if self.all_universes else "")
        self.story_type_menu = ctk.CTkOptionMenu(uni_frame, variable=self.story_type_var, values=list(self.all_universes.keys()))
        self.story_type_menu.pack(pady=5, padx=10, fill="x")

        self.custom_story_entry = ctk.CTkEntry(uni_frame, placeholder_text="Ou décris ton propre univers ici...")
        self.custom_story_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(uni_frame, text="Style Narratif :").pack(pady=(5,0))
        self.style_var = StringVar(value=list(self.all_styles.keys())[0] if self.all_styles else "")
        self.style_menu = ctk.CTkOptionMenu(uni_frame, variable=self.style_var, values=list(self.all_styles.keys()))
        self.style_menu.pack(pady=5, padx=10, fill="x")

        action_frame = ctk.CTkFrame(tab)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.start_button = ctk.CTkButton(action_frame, text="Démarrer l’aventure", command=self.start_game_async)
        self.start_button.pack(pady=5, padx=10, fill="x")
        self.restart_button = ctk.CTkButton(action_frame, text="Recommencer", command=self.start_game_async)
        self.restart_button.pack(pady=5, padx=10, fill="x")

    def _create_universes_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(tab, text="Gérer les Univers Personnalisés", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)

        form_frame = ctk.CTkFrame(tab)
        form_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Nom de l'univers :").pack(anchor="w", padx=10)
        self.custom_uni_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Cyberpunk Noir")
        self.custom_uni_name_entry.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(form_frame, text="Description (Prompt de départ) :").pack(anchor="w", padx=10)
        self.custom_uni_desc_textbox = ctk.CTkTextbox(form_frame, height=150)
        self.custom_uni_desc_textbox.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.custom_uni_desc_textbox.insert("0.0", "Exemple : Le héros, {hero_name}, est un détective privé...")

        button_frame = ctk.CTkFrame(tab)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)
        
        add_uni_button = ctk.CTkButton(button_frame, text="Ajouter/Modifier", command=self.add_or_update_custom_universe)
        add_uni_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        delete_uni_button = ctk.CTkButton(button_frame, text="Supprimer Sélectionné", command=self.delete_custom_universe)
        delete_uni_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _create_styles_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="Gérer les Styles Narratifs", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)

        form_frame = ctk.CTkFrame(tab)
        form_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Nom du style :").pack(anchor="w", padx=10)
        self.custom_style_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Ton Sarcastique")
        self.custom_style_name_entry.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(form_frame, text="Instruction pour l'IA :").pack(anchor="w", padx=10)
        self.custom_style_desc_textbox = ctk.CTkTextbox(form_frame, height=150)
        self.custom_style_desc_textbox.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.custom_style_desc_textbox.insert("0.0", "Exemple : Adopte un ton sarcastique et ironique...")

        button_frame = ctk.CTkFrame(tab)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)

        add_style_button = ctk.CTkButton(button_frame, text="Ajouter/Modifier", command=self.add_or_update_custom_style)
        add_style_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        delete_style_button = ctk.CTkButton(button_frame, text="Supprimer Sélectionné", command=self.delete_custom_style)
        delete_style_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _create_saves_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        sl_frame = ctk.CTkFrame(tab)
        sl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(sl_frame, text="Sauvegardes", font=ctk.CTkFont(weight="bold")).pack(pady=(5,10))

        self.save_button = ctk.CTkButton(sl_frame, text="Sauvegarder la partie actuelle", command=self.save_game)
        self.save_button.pack(pady=5, padx=10, fill="x")

        self.load_menu_var = StringVar(value="Choisir une sauvegarde")
        self.load_menu = ctk.CTkOptionMenu(sl_frame, variable=self.load_menu_var, values=[])
        self.load_menu.pack(pady=10, padx=10, fill="x")
        self.update_load_menu()

        self.load_button = ctk.CTkButton(sl_frame, text="Charger la sauvegarde", command=self.load_game)
        self.load_button.pack(pady=5, padx=10, fill="x")

        self.delete_button = ctk.CTkButton(sl_frame, text="Supprimer la sauvegarde", command=self.delete_save)
        self.delete_button.pack(pady=5, padx=10, fill="x")

    def log(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message + "\n\n")
        self.text.configure(state="disabled")
        self.text.see("end")

    def _on_mouse_wheel(self, event):
        if event.delta > 0: self.font_size += 1
        else: self.font_size -= 1
        self.font_size = max(8, min(30, self.font_size))
        self.text.configure(font=("Arial", self.font_size))

    def run_async(self, coro):
        asyncio.create_task(coro)

    def start_game_async(self):
        self.run_async(self.start_game())

    async def start_game(self):
        self.story_log.clear()
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        
        universe = self.story_type_var.get()
        custom = self.custom_story_entry.get().strip()
        style_name = self.style_var.get()
        style_instruction = self.all_styles.get(style_name, "Style par défaut.")
        self.hero_name = self.hero_name_entry.get().strip() or "Aventurier"

        if custom:
            base_prompt = f"Lance une aventure sur ce thème : {custom}. Le héros est {self.hero_name}."
        else:
            base_prompt = self.all_universes.get(universe, {}).get("prompt", "").replace("{hero_name}", self.hero_name)

        prompt_system = (
            f"{base_prompt}\n\n"
            "**Instructions strictes pour le Maître du Jeu (IA) :**\n"
            f"1.  **Style Narratif :** {style_instruction}\n"
            "2.  **Format de réponse :** Ta réponse doit TOUJOURS être une partie narrative suivie d'une liste de 4 choix numérotés (1. à 4.).\n"
            "3.  **Continuité :** L'histoire doit être cohérente avec les choix précédents.\n"
            "4.  **Ne jamais conclure :** L'aventure ne doit jamais se terminer. Propose toujours des choix pour continuer.\n"
            f"5.  **Héros :** Le personnage principal est et restera {self.hero_name}."
        )
        self.story_log.append({"role": "system", "content": prompt_system})
        self.log("Lancement de l'aventure...")
        await self.ask_ai("Commence l'aventure.", max_retries=3)

    # --- Generic Item Management ---
    def _add_or_update_item(self, name, description, item_dict, file_path, update_callback, item_type_name, name_entry, desc_textbox, is_structured=False):
        if not name or not description:
            self.log(f"[ERREUR] Le nom et la description de l'{item_type_name}' ne peuvent pas être vides.")
            return

        if is_structured:
            item_dict[name] = {"prompt": description}
        else:
            item_dict[name] = description
            
        _save_json_file(file_path, item_dict)
        update_callback()
        self.log(f"[INFO] {item_type_name.capitalize()} '{name}' ajouté/mis à jour.")
        name_entry.delete(0, "end")
        desc_textbox.delete("0.0", "end")

    def _delete_item(self, name_var, preset_dict, custom_dict, file_path, update_callback, item_type_name):
        name = name_var.get()
        if name in preset_dict:
            self.log(f"[ERREUR] Impossible de supprimer un {item_type_name} prédéfini.")
            return
        
        if name in custom_dict:
            del custom_dict[name]
            _save_json_file(file_path, custom_dict)
            update_callback()
            self.log(f"[INFO] {item_type_name.capitalize()} '{name}' supprimé.")
        else:
            self.log(f"[ERREUR] {item_type_name.capitalize()} personnalisé non trouvé ou non sélectionné.")

    # --- Universe Management ---
    def update_all_universes_menu(self):
        self.all_universes = {**self.preset_universes, **self.custom_universes}
        keys = list(self.all_universes.keys())
        self.story_type_menu.configure(values=keys)
        if keys: self.story_type_var.set(keys[0])

    def add_or_update_custom_universe(self):
        self._add_or_update_item(
            name=self.custom_uni_name_entry.get().strip(),
            description=self.custom_uni_desc_textbox.get("0.0", "end").strip(),
            item_dict=self.custom_universes,
            file_path=CUSTOM_UNIVERSES_FILE,
            update_callback=self.update_all_universes_menu,
            item_type_name="univers",
            name_entry=self.custom_uni_name_entry,
            desc_textbox=self.custom_uni_desc_textbox,
            is_structured=True
        )

    def delete_custom_universe(self):
        self._delete_item(self.story_type_var, self.preset_universes, self.custom_universes, CUSTOM_UNIVERSES_FILE, self.update_all_universes_menu, "univers")

    # --- Style Management ---
    def update_style_menu(self):
        self.all_styles = {**self.preset_styles, **self.custom_styles}
        keys = list(self.all_styles.keys())
        self.style_menu.configure(values=keys)
        if keys: self.style_var.set(keys[0])

    def add_or_update_custom_style(self):
        self._add_or_update_item(
            name=self.custom_style_name_entry.get().strip(),
            description=self.custom_style_desc_textbox.get("0.0", "end").strip(),
            item_dict=self.custom_styles,
            file_path=CUSTOM_STYLES_FILE,
            update_callback=self.update_style_menu,
            item_type_name="style",
            name_entry=self.custom_style_name_entry,
            desc_textbox=self.custom_style_desc_textbox
        )

    def delete_custom_style(self):
        self._delete_item(self.style_var, self.preset_styles, self.custom_styles, CUSTOM_STYLES_FILE, self.update_style_menu, "style")

    # --- AI Interaction ---
    async def ask_ai(self, user_input, is_continuation=False, max_retries=2, previous_response=None):
        if self.debug_mode: print(f"--- DEBUG INPUT (continuation={is_continuation}, retries={max_retries}) ---")

        if previous_response:
            prompt = f"Ta réponse précédente était invalide : '{previous_response}'. Corrige-la. Fournis une narration et 4 choix numérotés."
        elif is_continuation:
            prompt = "Continue l'histoire et propose 4 nouveaux choix."
        else:
            prompt = f"Le joueur choisit : '{user_input}'. Décris les conséquences et propose 4 nouveaux choix."
        
        if not previous_response: self.story_log.append({"role": "user", "content": prompt})

        data = {"model": "MythoMax 13B", "messages": self.story_log, "language": "French", "temperature": 0.9}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://app.ai4chat.co/api/v1/chat/completions", headers=HEADERS, json=data, timeout=45) as response:
                    response.raise_for_status()
                    message = (await response.json())['choices'][0]['message']['content']
                    self.story_log.append({"role": "assistant", "content": message})
                    text, choices = self.extract_choices(message)

                    if len(choices) == 4:
                        self.log(text)
                        self.update_choices(choices)
                    elif max_retries > 0:
                        self.log("Réponse de l'IA invalide. Nouvelle tentative...")
                        self.story_log.pop()
                        await self.ask_ai(user_input, is_continuation, max_retries - 1, previous_response=message)
                    else:
                        self.log("[Erreur Critique] L'IA n'a pas pu générer une réponse valide.")
                        self.update_choices([])

        except aiohttp.ClientError as e: self.log(f"[Erreur Réseau] {e}")
        except Exception as e:
            self.log(f"[Erreur Inattendue] {e}")
            if self.debug_mode: traceback.print_exc()

    def extract_choices(self, text):
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
        return "\n".join(narrative).strip(), choices

    def update_choices(self, choices):
        for widget in self.choices_frame.winfo_children(): widget.destroy()
        if choices:
            for choice_text in choices:
                b = ctk.CTkButton(self.choices_frame, text=choice_text, command=lambda c=choice_text: self.run_async(self.on_choice_click(c)))
                b.pack(pady=4, padx=10, fill="x")
        else:
            self.log("L'aventure est en pause. Cliquez sur 'Continuer' pour relancer l'IA.")
            b = ctk.CTkButton(self.choices_frame, text="Continuer", command=lambda: self.run_async(self.ask_ai("Continuer", is_continuation=True)))
            b.pack(pady=4, padx=10, fill="x")

    async def on_choice_click(self, choice):
        self.log(f"▶ Choix : {choice}")
        for widget in self.choices_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.choices_frame, text="L'IA réfléchit...").pack()
        await self.ask_ai(choice)

    # --- Save/Load Management ---
    def get_save_files(self):
        return [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

    def update_load_menu(self):
        saves = self.get_save_files() or ["Aucune sauvegarde"]
        self.load_menu.configure(values=saves)
        self.load_menu_var.set(saves[0])

    def save_game(self):
        if not self.story_log:
            self.log("[INFO] Impossible de sauvegarder une partie non commencée.")
            return
        save_name = simpledialog.askstring("Sauvegarder", "Nom de la sauvegarde :")
        if save_name:
            _save_json_file(os.path.join(SAVE_DIR, f"{save_name}.json"), self.story_log)
            self.log(f"[INFO] Partie sauvegardée sous : {save_name}")
            self.update_load_menu()

    def load_game(self):
        save_name = self.load_menu_var.get()
        if save_name == "Aucune sauvegarde": return
        file_path = os.path.join(SAVE_DIR, save_name)
        try:
            self.story_log = _load_json_file(file_path, None)
            if self.story_log is None:
                self.log(f"[ERREUR] Sauvegarde '{save_name}' vide ou corrompue.")
                return
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            for message in self.story_log:
                if message["role"] == "assistant": self.log(self.extract_choices(message["content"])[0])
            if self.story_log[-1]["role"] == "assistant": self.update_choices(self.extract_choices(self.story_log[-1]["content"])[1])
            self.log(f"[INFO] Partie '{save_name}' chargée.")
        except Exception as e:
            self.log(f"[ERREUR] Impossible de charger la sauvegarde : {e}")

    def delete_save(self):
        save_name = self.load_menu_var.get()
        if save_name == "Aucune sauvegarde": return
        try:
            os.remove(os.path.join(SAVE_DIR, save_name))
            self.log(f"[INFO] Sauvegarde '{save_name}' supprimée.")
            self.update_load_menu()
        except Exception as e:
            self.log(f"[ERREUR] Impossible de supprimer la sauvegarde : {e}")

if __name__ == "__main__":
    async def main():
        app = RPGApp()
        await app.run()
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run loop while another loop is running" not in str(e): raise
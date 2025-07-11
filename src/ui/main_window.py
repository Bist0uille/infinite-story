import customtkinter as ctk
from tkinter import StringVar, simpledialog
import asyncio
import re
import traceback
import os
import logging

from ..services.ai_service import AIClient
from ..services import data_service as dm
from ..core.engine import GameEngine

class AsyncioTk(ctk.CTk):
    """A CustomTkinter root window with an integrated asyncio event loop."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.running = True
        self.loop = asyncio.get_event_loop()

    def on_closing(self):
        logging.info("Application window closing.")
        self.running = False

    async def run(self):
        while self.running:
            self.update()
            await asyncio.sleep(0.01)

class RPGApp(AsyncioTk):
    """The main application class for the RPG adventure game."""
    def __init__(self):
        super().__init__()
        logging.info("Initializing RPGApp.")

        self.title("INFINITE STORY")
        self.geometry("1200x750")
        ctk.set_appearance_mode("Dark")

        # --- Game Engine ---
        self.game_engine = GameEngine()
        self.font_size = 14

        # --- AI Client ---
        self.ai = None
        self.ai_available = False
        try:
            self.ai = AIClient()
            self.ai_available = True
            logging.info("AI Client initialized successfully")
        except EnvironmentError as e:
            self._handle_ai_initialization_error(e)
        except Exception as e:
            logging.critical(f"Unexpected error initializing AIClient: {e}", exc_info=True)
            self._handle_ai_initialization_error(e)

        # --- Data Loading ---
        dm.init_default_files()
        if not os.path.exists(dm.SAVE_DIR):
            logging.info(f"Save directory '{dm.SAVE_DIR}' not found, creating it.")
            os.makedirs(dm.SAVE_DIR)
            
        self.preset_universes = dm.load_json(dm.PRESET_UNIVERSES_FILE)
        self.custom_universes = dm.load_json(dm.CUSTOM_UNIVERSES_FILE)
        self.preset_styles = dm.load_json(dm.PRESET_STYLES_FILE)
        self.custom_styles = dm.load_json(dm.CUSTOM_STYLES_FILE)
        
        self.all_universes = {**self.preset_universes, **self.custom_universes}
        self.all_styles = {**self.preset_styles, **self.custom_styles}

        self._build_ui()
        logging.info("UI built successfully.")

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
        # Bind scroll avec vérification Ctrl
        self.text.bind("<MouseWheel>", self._on_mousewheel_handler)
        self.text.bind("<Button-4>", self._on_mousewheel_handler)    # Linux scroll up
        self.text.bind("<Button-5>", self._on_mousewheel_handler)    # Linux scroll down

        self.choices_frame = ctk.CTkScrollableFrame(main_frame, label_text="Vos Choix")
        self.choices_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.choices_frame.bind("<Control-MouseWheel>", self._on_choices_font_change)
        self.choices_frame.bind("<Command-MouseWheel>", self._on_choices_font_change)

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
        self.hero_name_entry.insert(0, self.game_engine.hero_name)

        uni_frame = ctk.CTkFrame(tab)
        uni_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(uni_frame, text="Univers & Style", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        
        ctk.CTkLabel(uni_frame, text="Choix de l'univers : ").pack(pady=(5,0))
        self.story_type_var = StringVar(value=list(self.all_universes.keys())[0] if self.all_universes else "")
        self.story_type_menu = ctk.CTkOptionMenu(uni_frame, variable=self.story_type_var, values=list(self.all_universes.keys()))
        self.story_type_menu.pack(pady=5, padx=10, fill="x")

        self.custom_story_entry = ctk.CTkEntry(uni_frame, placeholder_text="Ou décris ton propre univers ici...")
        self.custom_story_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(uni_frame, text="Style Narratif : ").pack(pady=(5,0))
        self.style_var = StringVar(value=list(self.all_styles.keys())[0] if self.all_styles else "")
        self.style_menu = ctk.CTkOptionMenu(uni_frame, variable=self.style_var, values=list(self.all_styles.keys()))
        self.style_menu.pack(pady=5, padx=10, fill="x")

        action_frame = ctk.CTkFrame(tab)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.start_button = ctk.CTkButton(action_frame, text="Démarrer l'aventure", command=self.start_game_async)
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

        ctk.CTkLabel(form_frame, text="Nom de l'univers : ").pack(anchor="w", padx=10)
        self.custom_uni_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Cyberpunk Noir")
        self.custom_uni_name_entry.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(form_frame, text="Description (Prompt de départ) : ").pack(anchor="w", padx=10)
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

        ctk.CTkLabel(form_frame, text="Nom du style : ").pack(anchor="w", padx=10)
        self.custom_style_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Ton Sarcastique")
        self.custom_style_name_entry.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(form_frame, text="Instruction pour l'IA : ").pack(anchor="w", padx=10)
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

    def display_log(self, message):
        """Appends a message to the main text box in the UI."""
        self.text.configure(state="normal")
        self.text.insert("end", message + "\n\n")
        self.text.configure(state="disabled")
        self.text.see("end")

    def _on_mousewheel_handler(self, event):
        """Gère la molette : Ctrl = zoom, sinon = scroll normal"""
        # Vérifier si Ctrl est pressé
        if event.state & 0x4:  # 0x4 = Ctrl pressé
            # Zoom
            if hasattr(event, 'delta'):
                # Windows/Mac
                if event.delta > 0: self.font_size += 1
                else: self.font_size -= 1
            else:
                # Linux (Button-4 = scroll up, Button-5 = scroll down)
                if event.num == 4: self.font_size += 1
                elif event.num == 5: self.font_size -= 1
            
            self.font_size = max(8, min(30, self.font_size))
            self.text.configure(font=("Arial", self.font_size))
        else:
            # Scroll normal - laisser faire le comportement par défaut
            return None  # Permet le scroll normal

    def _on_choices_font_change(self, event):
        # Ctrl+scroll pour changer la taille du texte des choix
        if not hasattr(self, 'choices_font_size'):
            self.choices_font_size = 14
        
        if event.delta > 0: self.choices_font_size += 1
        else: self.choices_font_size -= 1
        self.choices_font_size = max(8, min(24, self.choices_font_size))
        
        # Mettre à jour tous les boutons existants
        for widget in self.choices_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(font=("Arial", self.choices_font_size))

    def run_async(self, coro):
        asyncio.create_task(coro)

    def start_game_async(self):
        logging.info("User clicked 'Start Adventure'.")
        self.run_async(self.start_game())

    async def start_game(self):
        if not self._check_ai_available():
            return
        
        self.game_engine.clear_game_state()
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        
        universe_name = self.story_type_var.get()
        custom_universe_prompt = self.custom_story_entry.get().strip()
        style_name = self.style_var.get()
        style_instruction = self.all_styles.get(style_name, "Style par défaut.")
        self.game_engine.set_hero_name(self.hero_name_entry.get())

        # --- Build the System Prompt ---
        if custom_universe_prompt:
            base_prompt = f"Lance une aventure sur ce thème : {custom_universe_prompt}. Le héros est {self.game_engine.hero_name}."
            logging.info(f"Starting game with custom universe. Hero: {self.game_engine.hero_name}, Prompt: {custom_universe_prompt}")
        else:
            base_prompt = self.all_universes.get(universe_name, {}).get("prompt", "").replace("{hero_name}", self.game_engine.hero_name)
            logging.info(f"Starting game with preset universe. Hero: {self.game_engine.hero_name}, Universe: {universe_name}")

        prompt_system = self.game_engine.build_system_prompt(base_prompt, style_instruction)
        
        self.game_engine.add_system_message(prompt_system)
        logging.debug(f"System prompt set: {prompt_system}")
        self.display_log("Lancement de l'aventure...")
        await self.ask_ai("Commence l'aventure.", max_retries=3)

    # --- Generic Item Management ---
    def _add_or_update_item(self, name, description, item_dict, file_path, update_callback, item_type_name, name_entry, desc_textbox, is_structured=False):
        if not name or not description:
            self.display_log(f"[ERREUR] Le nom et la description de l'{item_type_name}' ne peuvent pas être vides.")
            logging.warning(f"Attempted to add/update {item_type_name} with empty name or description.")
            return

        if is_structured:
            item_dict[name] = {"prompt": description}
        else:
            item_dict[name] = description
            
        dm.save_json(file_path, item_dict)
        update_callback()
        self.display_log(f"[INFO] {item_type_name.capitalize()} '{name}' ajouté/mis à jour.")
        logging.info(f"{item_type_name.capitalize()} '{name}' was added or updated.")
        name_entry.delete(0, "end")
        desc_textbox.delete("0.0", "end")

    def _delete_item(self, name_var, preset_dict, custom_dict, file_path, update_callback, item_type_name):
        name = name_var.get()
        if name in preset_dict:
            self.display_log(f"[ERREUR] Impossible de supprimer un {item_type_name} prédéfini.")
            logging.warning(f"Attempted to delete a preset {item_type_name}: {name}")
            return
        
        if name in custom_dict:
            logging.info(f"Deleting custom {item_type_name}: {name}")
            del custom_dict[name]
            dm.save_json(file_path, custom_dict)
            update_callback()
            self.display_log(f"[INFO] {item_type_name.capitalize()} '{name}' supprimé.")
        else:
            self.display_log(f"[ERREUR] {item_type_name.capitalize()} personnalisé non trouvé ou non sélectionné.")
            logging.warning(f"Attempted to delete non-existent custom {item_type_name}: {name}")

    # --- Universe Management ---
    def update_all_universes_menu(self):
        self.all_universes = {**self.preset_universes, **self.custom_universes}
        keys = list(self.all_universes.keys())
        self.story_type_menu.configure(values=keys)
        if keys: self.story_type_var.set(keys[0])
        logging.debug("Universe menu updated.")

    def add_or_update_custom_universe(self):
        name = self.custom_uni_name_entry.get().strip()
        logging.info(f"User clicked 'Add/Update Universe' for: {name}")
        self._add_or_update_item(
            name=name,
            description=self.custom_uni_desc_textbox.get("0.0", "end").strip(),
            item_dict=self.custom_universes,
            file_path=dm.CUSTOM_UNIVERSES_FILE,
            update_callback=self.update_all_universes_menu,
            item_type_name="univers",
            name_entry=self.custom_uni_name_entry,
            desc_textbox=self.custom_uni_desc_textbox,
            is_structured=True
        )

    def delete_custom_universe(self):
        name = self.story_type_var.get()
        logging.info(f"User clicked 'Delete Universe' for: {name}")
        self._delete_item(self.story_type_var, self.preset_universes, self.custom_universes, dm.CUSTOM_UNIVERSES_FILE, self.update_all_universes_menu, "univers")

    # --- Style Management ---
    def update_style_menu(self):
        self.all_styles = {**self.preset_styles, **self.custom_styles}
        keys = list(self.all_styles.keys())
        self.style_menu.configure(values=keys)
        if keys: self.style_var.set(keys[0])
        logging.debug("Style menu updated.")

    def add_or_update_custom_style(self):
        name = self.custom_style_name_entry.get().strip()
        description = self.custom_style_desc_textbox.get("0.0", "end").strip()
        logging.info(f"User clicked 'Add/Update Style' for: {name}")
        self._add_or_update_item(
            name=name,
            description=description,
            item_dict=self.custom_styles,
            file_path=dm.CUSTOM_STYLES_FILE,
            update_callback=self.update_style_menu,
            item_type_name="style",
            name_entry=self.custom_style_name_entry,
            desc_textbox=self.custom_style_desc_textbox
        )

    def delete_custom_style(self):
        name = self.style_var.get()
        logging.info(f"User clicked 'Delete Style' for: {name}")
        self._delete_item(self.style_var, self.preset_styles, self.custom_styles, dm.CUSTOM_STYLES_FILE, self.update_style_menu, "style")

    # --- AI Interaction ---
    async def _update_world_state(self, new_narrative):
        """Asks the AI to extract key facts from the new narrative."""
        if not new_narrative.strip():
            return

        prompt = (
            "Lis le paragraphe suivant et extrais les faits importants sous forme de 'clé: valeur'. "
            "Concentre-toi sur les noms des personnages (PNJ), leurs rôles ou caractéristiques, et les lieux importants. "
            "Écris chaque fait sur une ligne séparée. "
            "Utilise le format: [Nom/Lieu]: [description/caractéristique].\n\n"
            f"Paragraphe à analyser:\n{new_narrative}\n\n"
            "Réponse:"
        )
        
        try:
            # Use a simpler, faster model for this extraction if possible, or just the same one
            messages = [{"role": "user", "content": prompt}]
            raw_facts = await self.ai.complete(messages) # This assumes 'complete' can be used for such tasks
            
            self.game_engine.update_world_state_from_facts(raw_facts)

        except Exception as e:
            logging.error(f"Could not update world state: {e}", exc_info=True)


    async def ask_ai(self, user_input, is_continuation=False, max_retries=2, previous_response=None):
        logging.debug(f"ask_ai called. Input: '{user_input}', Continuation: {is_continuation}, Retries left: {max_retries}")

        prompt = self.game_engine.build_prompt_with_context(user_input, is_continuation, previous_response)
        
        if not previous_response:
            self.game_engine.add_user_message(prompt)
            logging.debug(f"Appended user message to story log: {prompt}")

        try:
            message = await self.ai.complete(self.game_engine.story_log)
            self.game_engine.add_assistant_message(message)
            text, choices = self.game_engine.extract_choices(message)

            if len(choices) == 4:
                self.display_log(text)
                self.update_choices(choices)
                # await self._update_world_state(text) # DISABLED: Causes MAX_TOKENS - TODO: Fix later
                logging.info("AI response was valid. Updated UI and world state.")
            elif max_retries > 0:
                self.display_log("Réponse de l'IA invalide. Nouvelle tentative...")
                logging.warning(f"Invalid AI response format. Retrying... (Retries left: {max_retries-1})")
                self.game_engine.remove_last_message()
                await self.ask_ai(user_input, is_continuation, max_retries - 1, previous_response=message)
            else:
                self.display_log("[Erreur Critique] L'IA n'a pas pu générer une réponse valide.")
                logging.error("AI failed to generate a valid response after all retries.")
                self.update_choices([])

        except Exception as e:
            self.display_log(f"[Erreur Inattendue] {e}")
            logging.critical(f"An unexpected error occurred in ask_ai: {e}", exc_info=True)

    def update_choices(self, choices):
        # Initialiser la taille de police des choix si nécessaire (augmentée de +2)
        if not hasattr(self, 'choices_font_size'):
            self.choices_font_size = 14
            
        for widget in self.choices_frame.winfo_children(): widget.destroy()
        if choices:
            for choice_text in choices:
                b = ctk.CTkButton(
                    self.choices_frame, 
                    text=choice_text, 
                    command=lambda c=choice_text: self.run_async(self.on_choice_click(c)),
                    font=("Arial", self.choices_font_size)
                )
                b.pack(pady=6, padx=10, fill="x")
        else:
            self.display_log("L'aventure est en pause. Cliquez sur 'Continuer' pour relancer l'IA.")
            b = ctk.CTkButton(
                self.choices_frame, 
                text="Continuer", 
                command=lambda: self.run_async(self.ask_ai("Continuer", is_continuation=True)),
                font=("Arial", self.choices_font_size)
            )
            b.pack(pady=6, padx=10, fill="x")
        logging.debug(f"Updated UI with {len(choices)} choices.")

    def _handle_ai_initialization_error(self, error):
        """Handle AI initialization errors gracefully"""
        self.ai_available = False
        error_msg = f"[ERREUR CRITIQUE] Impossible d'initialiser l'IA: {error}"
        logging.critical(f"AI initialization failed: {error}", exc_info=True)
        
        # Show error in UI
        self.display_log(error_msg)
        self.display_log("\n" + "="*50)
        self.display_log("L'application fonctionne en mode dégradé.")
        self.display_log("Vérifiez votre clé API GEMINI_API_KEY dans le fichier .env")
        self.display_log("Les fonctions d'histoire sont désactivées.")
        self.display_log("="*50 + "\n")
        
        # Disable AI-dependent features
        self._disable_ai_features()

    def _disable_ai_features(self):
        """Disable features that require AI when AI is unavailable"""
        # This will be called from _build_ui, so we need to handle it there
        pass

    def _check_ai_available(self):
        """Check if AI is available before AI operations"""
        if not self.ai_available:
            self.display_log("[ERREUR] Fonctionnalité indisponible - IA non initialisée")
            return False
        return True

    def _show_loading_indicator(self, message="Chargement..."):
        """Show loading indicator in choices area"""
        for widget in self.choices_frame.winfo_children(): 
            widget.destroy()
        loading_label = ctk.CTkLabel(
            self.choices_frame, 
            text=message, 
            font=("Arial", 14, "italic")
        )
        loading_label.pack(pady=10)

    def _hide_loading_indicator(self):
        """Hide loading indicator - choices will be updated by caller"""
        pass  # Choices update will clear the loading indicator

    def _handle_ai_error(self, error):
        """Handle AI errors gracefully during gameplay"""
        logging.error(f"AI error during gameplay: {error}", exc_info=True)
        self.display_log(f"[ERREUR IA] {error}")
        
        # Show error in choices area
        for widget in self.choices_frame.winfo_children(): 
            widget.destroy()
        error_label = ctk.CTkLabel(
            self.choices_frame, 
            text="Erreur IA - Réessayez ou redémarrez l'aventure",
            text_color="red"
        )
        error_label.pack(pady=10)
        
        retry_button = ctk.CTkButton(
            self.choices_frame,
            text="Réessayer",
            command=lambda: self.run_async(self.ask_ai("Continuer", is_continuation=True))
        )
        retry_button.pack(pady=5)

    async def on_choice_click(self, choice):
        if not self._check_ai_available():
            return
            
        logging.info(f"User chose: '{choice}'")
        self.display_log(f"▶ Choix : {choice}")
        # Show loading indicator
        self._show_loading_indicator("L'IA réfléchit...")
        try:
            await self.ask_ai(choice)
        except Exception as e:
            self._handle_ai_error(e)
        finally:
            self._hide_loading_indicator()

    # --- Save/Load Management ---
    def get_save_files(self):
        return [f for f in os.listdir(dm.SAVE_DIR) if f.endswith(".json")]

    def update_load_menu(self):
        saves = self.get_save_files() or ["Aucune sauvegarde"]
        self.load_menu.configure(values=saves)
        self.load_menu_var.set(saves[0])
        logging.debug("Load menu updated.")

    def save_game(self):
        if not self.game_engine.story_log:
            self.display_log("[INFO] Impossible de sauvegarder une partie non commencée.")
            logging.warning("Attempted to save a game that has not started.")
            return
        save_name = simpledialog.askstring("Sauvegarder", "Nom de la sauvegarde :")
        if save_name:
            logging.info(f"User is saving the game as '{save_name}'.")
            save_data = self.game_engine.get_save_data()
            dm.save_json(os.path.join(dm.SAVE_DIR, f"{save_name}.json"), save_data)
            self.display_log(f"[INFO] Partie sauvegardée sous : {save_name}")
            self.update_load_menu()
        else:
            logging.info("User cancelled the save dialog.")

    def load_game(self):
        save_name = self.load_menu_var.get()
        if save_name == "Aucune sauvegarde": return
        logging.info(f"User is loading game: '{save_name}'")
        file_path = os.path.join(dm.SAVE_DIR, save_name)
        try:
            save_data = dm.load_json(file_path, None)
            if save_data is None:
                self.display_log(f"[ERREUR] Sauvegarde '{save_name}' vide ou corrompue.")
                logging.error(f"Save file '{save_name}' is empty or corrupted.")
                return
            
            self.game_engine.load_game_state(save_data)

            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            # Re-populate the story display from the loaded log
            for message in self.game_engine.story_log:
                if message["role"] == "assistant":
                    self.display_log(self.game_engine.extract_choices(message["content"])[0])
            
            # Set up the next choices
            narrative, choices = self.game_engine.get_last_narrative_and_choices()
            if choices:
                self.update_choices(choices)

            self.display_log(f"[INFO] Partie '{save_name}' chargée.")
            logging.info(f"Game '{save_name}' loaded successfully. World state: {self.game_engine.world_state}")
        except Exception as e:
            self.display_log(f"[ERREUR] Impossible de charger la sauvegarde : {e}")
            logging.error(f"Failed to load save '{save_name}': {e}", exc_info=True)

    def delete_save(self):
        save_name = self.load_menu_var.get()
        if save_name == "Aucune sauvegarde": return
        logging.info(f"User is deleting save: '{save_name}'")
        try:
            os.remove(os.path.join(dm.SAVE_DIR, save_name))
            self.display_log(f"[INFO] Sauvegarde '{save_name}' supprimée.")
            self.update_load_menu()
        except Exception as e:
            self.display_log(f"[ERREUR] Impossible de supprimer la sauvegarde : {e}")
            logging.error(f"Failed to delete save '{save_name}': {e}", exc_info=True)
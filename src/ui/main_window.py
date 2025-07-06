

import customtkinter as ctk
from tkinter import StringVar, simpledialog
import asyncio
import os
import logging

from services.ai_service import AIClient
from services import data_service as dm
from core.engine import GameEngine

class AsyncioTk(ctk.CTk):
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
    def __init__(self):
        super().__init__()
        logging.info("Initializing RPGApp.")
        self.title("INFINITE STORY")
        self.geometry("1200x750")
        ctk.set_appearance_mode("Dark")
        
        # Override close handler to log session summary
        self.protocol("WM_DELETE_WINDOW", self.on_closing_with_summary)

        self.ai = None
        self.ai_available = False
        try:
            self.ai = AIClient()
            self.ai.start_session()  # Start token tracking
            self.ai_available = True
        except Exception as e:
            self._handle_ai_initialization_error(e)

        self.game_engine = GameEngine(self.ai)
        self.font_size = 14

        dm.init_default_files()
        if not os.path.exists(dm.SAVE_DIR):
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

        self.choices_frame = ctk.CTkScrollableFrame(main_frame, label_text="Vos Choix")
        self.choices_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Right Panel ---
        control_panel = ctk.CTkFrame(self)
        control_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        control_panel.grid_columnconfigure(0, weight=1)
        control_panel.grid_rowconfigure(0, weight=1) # Tabs will take most space

        # --- Tabs ---
        tab_view = ctk.CTkTabview(control_panel, anchor="w")
        tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self._create_play_tab(tab_view.add("▶ Jouer"))
        self._create_universes_tab(tab_view.add("🌌 Univers"))
        self._create_styles_tab(tab_view.add("🎨 Styles"))
        self._create_saves_tab(tab_view.add("💾 Sauvegardes"))

        # --- World State Display ---
        world_display_frame = ctk.CTkFrame(control_panel, border_width=1)
        world_display_frame.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        world_display_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(world_display_frame, text="État du Monde", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(world_display_frame, text="👤 Héros:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=5)
        self.hero_name_label = ctk.CTkLabel(world_display_frame, text="N/A", anchor="w")
        self.hero_name_label.grid(row=1, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(world_display_frame, text="❤️ Statut:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=5)
        self.hero_status_label = ctk.CTkLabel(world_display_frame, text="N/A", anchor="w")
        self.hero_status_label.grid(row=2, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(world_display_frame, text="📍 Lieu:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=5)
        self.location_label = ctk.CTkLabel(world_display_frame, text="N/A", anchor="w", wraplength=250)
        self.location_label.grid(row=3, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(world_display_frame, text="👥 PNJ:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", padx=5)
        self.npcs_label = ctk.CTkLabel(world_display_frame, text="Aucun", anchor="w", wraplength=250)
        self.npcs_label.grid(row=4, column=1, sticky="ew", padx=5)

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
        self.story_type_var = StringVar(value=list(self.all_universes.keys())[0] if self.all_universes else "")
        self.story_type_menu = ctk.CTkOptionMenu(uni_frame, variable=self.story_type_var, values=list(self.all_universes.keys()))
        self.story_type_menu.pack(pady=5, padx=10, fill="x")
        self.custom_story_entry = ctk.CTkEntry(uni_frame, placeholder_text="Ou décris ton propre univers ici...")
        self.custom_story_entry.pack(pady=5, padx=10, fill="x")
        self.style_var = StringVar(value=list(self.all_styles.keys())[0] if self.all_styles else "")
        self.style_menu = ctk.CTkOptionMenu(uni_frame, variable=self.style_var, values=list(self.all_styles.keys()))
        self.style_menu.pack(pady=5, padx=10, fill="x")

        action_frame = ctk.CTkFrame(tab)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.start_button = ctk.CTkButton(action_frame, text="Démarrer l'aventure", command=self.start_game_async)
        self.start_button.pack(pady=5, padx=10, fill="x")

    def update_world_display(self):
        ws = self.game_engine.world_state
        hero = ws.characters.get("main_character")
        
        if hero:
            self.hero_name_label.configure(text=hero.name)
            self.hero_status_label.configure(text=hero.status.capitalize())
            current_loc = ws.locations.get(hero.location_id)
            self.location_label.configure(text=current_loc.name if current_loc else "Inconnu")
        
        npcs = [c.name for i, c in ws.characters.items() if i != "main_character"]
        self.npcs_label.configure(text=", ".join(npcs) if npcs else "Aucun")
        logging.info("World display updated.")

    async def ask_ai(self, user_input, is_continuation=False, max_retries=2, previous_response=None):
        if not self._check_ai_available(): return

        prompt = self.game_engine.build_prompt_with_context(user_input, is_continuation, previous_response)
        if not previous_response:
            self.game_engine.add_user_message(prompt)

        try:
            message = await self.ai.complete(self.game_engine.get_story_log_for_api(), self.game_engine.world_state, "story_generation")
            self.game_engine.add_assistant_message(message)
            narrative, choices = self.game_engine.extract_choices(message)

            if len(choices) == 4:
                self.display_log(narrative)
                self.update_choices(choices)
                await self.game_engine.update_world_state_from_narrative(narrative)
                self.update_world_display()
            elif max_retries > 0:
                await self.ask_ai(user_input, is_continuation, max_retries - 1, previous_response=message)
            else:
                self.display_log("[Erreur Critique] L'IA n'a pas pu générer une réponse valide.")
                self.update_choices([])
        except Exception as e:
            self._handle_ai_error(e)

    def run_async(self, coro):
        asyncio.create_task(coro)

    def start_game_async(self):
        self.run_async(self.start_game())

    async def start_game(self):
        if not self._check_ai_available(): return
        
        self.game_engine.clear_game_state()
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        
        self.game_engine.set_hero_name(self.hero_name_entry.get())
        
        custom_prompt = self.custom_story_entry.get().strip()
        if custom_prompt:
            base_prompt = f"Lance une aventure sur ce thème : {custom_prompt}. Le héros est {self.game_engine.hero_name}."
        else:
            universe_name = self.story_type_var.get()
            base_prompt = self.all_universes.get(universe_name, {}).get("prompt", "").replace("{hero_name}", self.game_engine.hero_name)
        
        style_name = self.style_var.get()
        style_instruction = self.all_styles.get(style_name, "Style par défaut.")
        
        system_prompt = self.game_engine.build_system_prompt(base_prompt, style_instruction)
        self.game_engine.add_system_message(system_prompt)
        
        self.display_log("Lancement de l'aventure...")
        self.update_world_display()
        await self.ask_ai("Commence l'aventure.", max_retries=3)

    async def on_choice_click(self, choice):
        if not self._check_ai_available(): return
        self.display_log(f"▶ Choix : {choice}")
        self._show_loading_indicator("L'IA réfléchit...")
        try:
            await self.ask_ai(choice)
        except Exception as e:
            self._handle_ai_error(e)
        finally:
            self._hide_loading_indicator()

    def update_choices(self, choices):
        for widget in self.choices_frame.winfo_children(): widget.destroy()
        if choices:
            for choice_text in choices:
                b = ctk.CTkButton(self.choices_frame, text=choice_text, command=lambda c=choice_text: self.run_async(self.on_choice_click(c)))
                b.pack(pady=6, padx=10, fill="x")
        else:
            b = ctk.CTkButton(self.choices_frame, text="Continuer", command=lambda: self.run_async(self.ask_ai("Continuer", is_continuation=True)))
            b.pack(pady=6, padx=10, fill="x")

    def _create_universes_tab(self, tab):
        # This can be filled in later if needed
        pass
    def _create_styles_tab(self, tab):
        # This can be filled in later if needed
        pass
    def _create_saves_tab(self, tab):
        # This can be filled in later if needed
        pass
    def display_log(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message + "\n\n")
        self.text.configure(state="disabled")
        self.text.see("end")
    def _on_mousewheel_handler(self, event):
        # Basic scroll, can be enhanced later
        pass
    def _handle_ai_initialization_error(self, error):
        self.ai_available = False
        self.display_log(f"Erreur AI: {error}")
    def _check_ai_available(self):
        return self.ai_available
    def _show_loading_indicator(self, message="Chargement..."):
        for widget in self.choices_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.choices_frame, text=message).pack()
    def _hide_loading_indicator(self):
        for widget in self.choices_frame.winfo_children(): widget.destroy()
    def _handle_ai_error(self, error):
        self.display_log(f"Erreur IA: {error}")
        self.update_choices([])
    
    def on_closing_with_summary(self):
        """Handle application closing with token usage summary."""
        logging.info("Application closing - generating session summary...")
        
        # Log session summary if AI client is available
        if self.ai and self.ai_available:
            try:
                self.ai.log_session_summary()
            except Exception as e:
                logging.error(f"Failed to log session summary: {e}")
        
        # Call original close handler
        self.on_closing()
    
    def save_game(self):
        pass
    def load_game(self):
        pass
    def delete_save(self):
        pass

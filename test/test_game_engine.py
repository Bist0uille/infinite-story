#!/usr/bin/env python3
"""
Test script pour analyser le GameEngine sans interface utilisateur.
Simule une session de jeu complète pour analyser :
- Construction du prompt système
- Gestion de l'historique
- Extraction des choix
- Gestion du world_state
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import GameEngine
from src.services.data_service import load_json, PRESET_UNIVERSES_FILE, PRESET_STYLES_FILE
from src.utils.logger_config import setup_logging
import logging

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f" {title}")
        print("="*80)

def analyze_game_engine():
    """Analyse complète du GameEngine"""
    setup_logging()
    
    print_separator("ANALYSE DU GAME ENGINE - SESSION DE TEST")
    
    # 1. Initialisation du moteur
    engine = GameEngine()
    print(f"✅ GameEngine initialisé")
    print(f"   - Hero name par défaut: '{engine.hero_name}'")
    print(f"   - Story log vide: {len(engine.story_log)} messages")
    print(f"   - World state vide: {len(engine.world_state)} éléments")
    
    # 2. Chargement des données
    preset_universes = load_json(PRESET_UNIVERSES_FILE, {})
    preset_styles = load_json(PRESET_STYLES_FILE, {})
    
    print_separator("DONNÉES CHARGÉES")
    print(f"✅ Univers prédéfinis: {list(preset_universes.keys())}")
    print(f"✅ Styles prédéfinis: {list(preset_styles.keys())}")
    
    # 3. Configuration du jeu
    engine.set_hero_name("Aeliana")
    universe_name = "Fantasy Classique"
    style_name = "Dramatique"
    
    base_prompt = preset_universes[universe_name]["prompt"].replace("{hero_name}", engine.hero_name)
    style_instruction = preset_styles[style_name]
    
    print_separator("CONFIGURATION DE LA SESSION")
    print(f"✅ Nom du héros: '{engine.hero_name}'")
    print(f"✅ Univers choisi: '{universe_name}'")
    print(f"✅ Style narratif: '{style_name}'")
    
    # 4. Construction du prompt système
    system_prompt = engine.build_system_prompt(base_prompt, style_instruction)
    engine.add_system_message(system_prompt)
    
    print_separator("PROMPT SYSTÈME CONSTRUIT")
    print("📝 Contenu du prompt système:")
    print("-" * 50)
    print(system_prompt)
    print("-" * 50)
    print(f"✅ Longueur: {len(system_prompt)} caractères")
    print(f"✅ Messages dans story_log: {len(engine.story_log)}")
    
    # 5. Simulation de réponses IA (sans vraie IA)
    print_separator("SIMULATION D'UNE SESSION DE JEU")
    
    # Première réponse IA simulée
    ai_response_1 = """Aeliana se réveille dans une taverne brumeuse, la tête lourde et les souvenirs flous. Autour d'elle, des murmures inquiétants s'élèvent : "Elle porte la marque..." "Les Gardiens la cherchent..." "Il faut qu'elle parte, maintenant !" 
    
Un homme encapuchonné s'approche discrètement, glissant un parchemin scellé dans sa main tremblante. "Votre destin vous attend au-delà des Monts Oubliés", chuchote-t-il avant de disparaître dans l'ombre.

1. Examiner immédiatement le parchemin dans la taverne
2. Fuir discrètement par la porte arrière
3. Confronter les clients qui murmurent à votre sujet
4. Demander refuge au tavernier et révéler votre identité"""

    print("🎭 RÉPONSE IA SIMULÉE #1:")
    print("-" * 50)
    print(ai_response_1)
    print("-" * 50)
    
    # Test d'extraction des choix
    engine.add_assistant_message(ai_response_1)
    narrative, choices = engine.extract_choices(ai_response_1)
    
    print("\n📊 ANALYSE DE L'EXTRACTION:")
    print(f"✅ Narrative extraite ({len(narrative)} caractères):")
    print(f"   {narrative[:100]}...")
    print(f"✅ Choix extraits ({len(choices)}):")
    for i, choice in enumerate(choices, 1):
        print(f"   {i}. {choice}")
    
    # 6. Simulation d'un choix utilisateur
    user_choice = "Examiner immédiatement le parchemin dans la taverne"
    prompt_with_context = engine.build_prompt_with_world_state(user_choice)
    engine.add_user_message(prompt_with_context)
    
    print_separator("CHOIX UTILISATEUR ET PROMPT GÉNÉRÉ")
    print(f"🎯 Choix utilisateur: '{user_choice}'")
    print(f"📝 Prompt généré avec contexte:")
    print("-" * 50)
    print(prompt_with_context)
    print("-" * 50)
    
    # 7. Simulation de mise à jour du world_state
    print_separator("SIMULATION WORLD STATE")
    
    # Simulation de faits extraits
    simulated_facts = """Taverne: Lieu mystérieux où Aeliana s'est réveillée
Homme encapuchonné: Mystérieux messager qui a donné un parchemin
Parchemin scellé: Document important lié au destin d'Aeliana
Monts Oubliés: Destination mentionnée par l'homme encapuchonné
Les Gardiens: Groupe qui recherche Aeliana
La marque: Signe distinctif porté par Aeliana"""
    
    engine.update_world_state_from_facts(simulated_facts)
    
    print("🌍 WORLD STATE MIS À JOUR:")
    for key, value in engine.world_state.items():
        print(f"   • {key}: {value}")
    
    # 8. Deuxième tour avec world_state
    ai_response_2 = """Le parchemin révèle une carte ancienne marquée de symboles runiques. Soudain, des gardes en armure noire font irruption dans la taverne ! "Livrez-nous celle qui porte la Marque du Dragon !" rugit leur capitaine.

Le tavernier, un vieil homme aux yeux perçants, murmure : "Passe par les caves, Aeliana. Le tunnel mène aux docks."

1. Suivre le conseil du tavernier et fuir par les caves
2. Affronter courageusement les gardes avec la magie de votre marque
3. Négocier avec le capitaine en révélant votre véritable identité
4. Créer une distraction en renversant les tonneaux d'alcool"""

    print_separator("DEUXIÈME RÉPONSE IA AVEC CONTEXTE")
    print("🎭 RÉPONSE IA SIMULÉE #2:")
    print("-" * 50)
    print(ai_response_2)
    print("-" * 50)
    
    engine.add_assistant_message(ai_response_2)
    narrative_2, choices_2 = engine.extract_choices(ai_response_2)
    
    print(f"✅ Nouveaux choix extraits ({len(choices_2)}):")
    for i, choice in enumerate(choices_2, 1):
        print(f"   {i}. {choice}")
    
    # Test avec world_state
    user_choice_2 = "Suivre le conseil du tavernier et fuir par les caves"
    prompt_with_state = engine.build_prompt_with_world_state(user_choice_2)
    
    print_separator("PROMPT AVEC WORLD STATE")
    print("📝 Prompt incluant le world state:")
    print("-" * 50)
    print(prompt_with_state)
    print("-" * 50)
    
    # 9. Test de sauvegarde/chargement
    print_separator("TEST SAUVEGARDE/CHARGEMENT")
    
    save_data = engine.get_save_data()
    print(f"✅ Données de sauvegarde générées:")
    print(f"   - Story log: {len(save_data['story_log'])} messages")
    print(f"   - World state: {len(save_data['world_state'])} éléments")
    
    # Nouveau moteur pour test de chargement
    engine_loaded = GameEngine()
    engine_loaded.load_game_state(save_data)
    
    print(f"✅ Test de chargement:")
    print(f"   - Story log chargé: {len(engine_loaded.story_log)} messages")
    print(f"   - World state chargé: {len(engine_loaded.world_state)} éléments")
    print(f"   - Cohérence: {engine.world_state == engine_loaded.world_state}")
    
    # 10. Analyse finale
    print_separator("ANALYSE FINALE")
    
    final_narrative, final_choices = engine_loaded.get_last_narrative_and_choices()
    
    print("📊 RÉSUMÉ DE LA SESSION:")
    print(f"   • Total messages: {len(engine.story_log)}")
    print(f"   • Éléments world_state: {len(engine.world_state)}")
    print(f"   • Dernière narrative: {len(final_narrative)} caractères")
    print(f"   • Derniers choix: {len(final_choices)}")
    print(f"   • Hero name: '{engine.hero_name}'")
    
    print("\n🎯 FONCTIONNALITÉS TESTÉES:")
    print("   ✅ Construction de prompt système")
    print("   ✅ Gestion de l'historique (story_log)")
    print("   ✅ Extraction narrative/choix")
    print("   ✅ World state dynamique")
    print("   ✅ Sauvegarde/chargement")
    print("   ✅ Cohérence des données")

if __name__ == "__main__":
    analyze_game_engine()
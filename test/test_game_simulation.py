

import sys
sys.path.insert(0, 'src')

from core.engine import GameEngine
from services.migration_service import MigrationService

def simulate_game(hero_name, universe):
    """Simulates a 5-turn game and returns the final WorldState."""
    engine = GameEngine()
    engine.clear_game_state()
    engine.set_hero_name(hero_name)
    system_prompt = engine.build_system_prompt(universe, "Style direct et clair")
    engine.add_system_message(system_prompt)
    engine.add_user_message(f"Je m'appelle {hero_name}. {universe}")

    # Initial AI response
    engine.add_assistant_message(
        "Vous vous trouvez à l'orée d'une forêt ancienne. Un chemin s'enfonce dans les bois sombres.\n"
        "1. Suivre le chemin\n"
        "2. Examiner les environs\n"
        "3. Grimper à un arbre\n"
        "4. Crier pour voir si quelqu'un répond"
    )

    for i in range(5):
        _, choices = engine.get_last_narrative_and_choices()
        if not choices:
            # Handle cases where no choices are available
            ai_response = "L'aventure semble être dans une impasse. Vous ne voyez aucune option claire."
        else:
            player_choice = choices[0]
            engine.add_user_message(player_choice)
            # Mock AI response - in a real scenario, this would come from the AI service
            ai_response = f"En réponse à '{player_choice}', vous avancez. Devant vous se trouve un nouveau défi.\n1. Option A\n2. Option B\n3. Option C\n4. Option D"
        
        engine.add_assistant_message(ai_response)

    migration_service = MigrationService()
    final_world_state = migration_service.migrate_from_story_log(engine.story_log, hero_name)
    return final_world_state

def main():
    """Runs two game simulations and prints the resulting WorldStates."""
    print("=== Simulation 1: Arthur dans la Forêt Enchantée ===")
    world_state_1 = simulate_game("Arthur", "une forêt enchantée")
    print(world_state_1.to_json())

    print("\n=== Simulation 2: Léna dans les Ruines Perdues ===")
    world_state_2 = simulate_game("Léna", "des ruines perdues")
    print(world_state_2.to_json())

if __name__ == "__main__":
    main()


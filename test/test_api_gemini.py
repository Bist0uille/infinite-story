"""
Test script for Gemini API functionality.
Tests API connection, model functionality, and entity extraction.
"""

import asyncio
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ai_service import AIClient
from core.engine import GameEngine


async def test_basic_api_connection():
    """Test basic API connection and response."""
    print("=== Testing Basic API Connection ===")
    
    try:
        ai_client = AIClient()
        print(f"✓ AIClient initialized with model: {ai_client.model}")
        
        # Simple test message
        messages = [
            {"role": "user", "content": "Dis juste 'Bonjour' pour tester la connexion."}
        ]
        
        response = await ai_client.complete(messages, "connection_test")
        print(f"✓ API Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Connection Test Failed: {e}")
        return False


async def test_story_generation():
    """Test story generation functionality."""
    print("\n=== Testing Story Generation ===")
    
    try:
        ai_client = AIClient()
        
        # Story generation test
        messages = [
            {"role": "system", "content": "Tu es un maître de jeu pour un RPG fantasy. Raconte une histoire courte avec 4 choix numérotés."},
            {"role": "user", "content": "Commence une aventure fantasy avec le héros Aiden dans une forêt mystérieuse."}
        ]
        
        response = await ai_client.complete(messages, "story_test")
        print(f"✓ Story Generated ({len(response)} characters):")
        print(f"Preview: {response[:200]}...")
        
        # Check if response contains numbered choices
        lines = response.split('\n')
        numbered_lines = [line for line in lines if any(line.strip().startswith(f"{i}.") or line.strip().startswith(f"{i})") for i in range(1, 5))]
        
        if len(numbered_lines) >= 4:
            print("✓ Story contains numbered choices")
        else:
            print(f"⚠️ Story may not have proper choices (found {len(numbered_lines)} numbered lines)")
        
        return True
        
    except Exception as e:
        print(f"❌ Story Generation Test Failed: {e}")
        return False


async def test_entity_extraction():
    """Test entity extraction functionality."""
    print("\n=== Testing Entity Extraction ===")
    
    try:
        ai_client = AIClient()
        game_engine = GameEngine(ai_client)
        
        # Test narrative with characters and locations
        test_narrative = """
        Aiden entre dans la taverne 'Le Dragon Endormi'. Le barman Marcus l'accueille avec un sourire.
        Dans un coin, une mystérieuse femme en cape noire, Lyanna, observe discrètement.
        La taverne est située dans le village de Pierrefond, près de la Forêt Sombre.
        """
        
        print(f"Testing with narrative: {test_narrative}")
        
        # Extract entities
        entities = await game_engine._extract_entities_from_narrative(test_narrative)
        print(f"✓ Entities extracted: {entities}")
        
        # Validate extraction
        expected_characters = ["marcus", "lyanna"]
        expected_locations = ["dragon endormi", "pierrefond", "forêt sombre"]
        
        found_characters = [char["name"].lower() for char in entities.get("characters", [])]
        found_locations = [loc["name"].lower() for loc in entities.get("locations", [])]
        
        print(f"Found characters: {found_characters}")
        print(f"Found locations: {found_locations}")
        
        character_match = any(char in " ".join(found_characters) for char in expected_characters)
        location_match = any(loc in " ".join(found_locations) for loc in expected_locations)
        
        if character_match:
            print("✓ Character extraction working")
        else:
            print("⚠️ Character extraction may need improvement")
            
        if location_match:
            print("✓ Location extraction working")
        else:
            print("⚠️ Location extraction may need improvement")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity Extraction Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_world_state_integration():
    """Test WorldState integration."""
    print("\n=== Testing WorldState Integration ===")
    
    try:
        ai_client = AIClient()
        game_engine = GameEngine(ai_client)
        
        # Initialize game
        game_engine.set_hero_name("Aiden")
        
        print(f"✓ Game initialized with hero: {game_engine.hero_name}")
        print(f"✓ Initial world state: {game_engine.world_state.get_world_summary()}")
        
        # Test adding system message
        game_engine.add_system_message("Tu es un maître de jeu RPG.")
        
        # Test adding user message
        game_engine.add_user_message("Je veux explorer la forêt.")
        
        # Simulate AI response
        game_engine.add_assistant_message("Tu entres dans une forêt sombre. Choix: 1) Avancer 2) Écouter 3) Grimper 4) Reculer")
        
        print(f"✓ Timeline has {len(game_engine.world_state.timeline)} events")
        print(f"✓ Current turn: {game_engine.get_current_turn_number()}")
        
        # Test story log generation
        story_log = game_engine.get_story_log_for_api()
        print(f"✓ Story log has {len(story_log)} messages")
        
        for i, msg in enumerate(story_log):
            print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ WorldState Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_game_cycle():
    """Test a complete game cycle."""
    print("\n=== Testing Full Game Cycle ===")
    
    try:
        ai_client = AIClient()
        game_engine = GameEngine(ai_client)
        
        # Setup game
        game_engine.set_hero_name("TestHero")
        game_engine.add_system_message("Aventure fantasy avec TestHero. Style: direct. Format: histoire + 4 choix.")
        
        # First AI call
        story_log = game_engine.get_story_log_for_api()
        game_engine.add_user_message("Commence l'aventure dans une forêt.")
        
        print("Making first AI call...")
        story_log = game_engine.get_story_log_for_api()
        ai_response = await ai_client.complete(story_log, "full_cycle_test")
        
        game_engine.add_assistant_message(ai_response)
        narrative, choices = game_engine.extract_choices(ai_response)
        
        print(f"✓ First response received")
        print(f"✓ Narrative: {narrative[:100]}...")
        print(f"✓ Choices found: {len(choices)}")
        for i, choice in enumerate(choices):
            print(f"  {i+1}. {choice}")
        
        # Test entity extraction on the narrative
        print("Testing entity extraction on generated narrative...")
        await game_engine.update_world_state_from_narrative(narrative)
        
        updated_summary = game_engine.world_state.get_world_summary()
        print(f"✓ Updated world state: {updated_summary}")
        
        if len(choices) == 4:
            print("✓ Full game cycle working correctly")
            return True
        else:
            print(f"⚠️ Expected 4 choices, got {len(choices)}")
            return False
        
    except Exception as e:
        print(f"❌ Full Game Cycle Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all API tests."""
    print("🧪 Starting Gemini API Tests...\n")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        ("Basic API Connection", test_basic_api_connection),
        ("Story Generation", test_story_generation),
        ("Entity Extraction", test_entity_extraction),
        ("WorldState Integration", test_world_state_integration),
        ("Full Game Cycle", test_full_game_cycle),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! API is fully functional.")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
"""
Test script for WorldState serialization/deserialization.
This script tests the Pydantic models and migration functionality.
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from models.world_state import WorldState, Character, Location, Event
from services.migration_service import MigrationService


def test_world_state_creation():
    """Test creating a WorldState from scratch."""
    print("=== Testing WorldState Creation ===")
    
    # Create a new world state
    world_state = WorldState()
    
    # Add a character
    character = Character(
        id="test_char",
        name="Test Character",
        traits=["brave", "curious"],
        status="alive",
        location_id="test_location",
        arcs=["test_arc"]
    )
    world_state.add_character(character)
    
    # Add a location
    location = Location(
        id="test_location",
        name="Test Location",
        tags=["fantasy", "forest"],
        description="A mystical forest clearing"
    )
    world_state.add_location(location)
    
    # Add an event
    event = Event(
        id="test_event",
        descr="The adventure begins",
        ts=1,
        impact={"type": "story_start"}
    )
    world_state.add_event(event)
    
    # Test some operations
    world_state.set_flag("test_flag", True)
    world_state.add_to_inventory("sword")
    
    print(f"V Created WorldState with {len(world_state.characters)} character(s)")
    print(f"V Created WorldState with {len(world_state.locations)} location(s)")
    print(f"V Created WorldState with {len(world_state.timeline)} event(s)")
    print(f"V Flags: {world_state.flags}")
    print(f"V Inventory: {world_state.inventory}")
    
    return world_state


def test_serialization(world_state):
    """Test JSON serialization and deserialization."""
    print("\n=== Testing Serialization ===")
    
    # Serialize to JSON
    json_data = world_state.to_json()
    print(f"V Serialized WorldState to JSON ({len(json_data)} characters)")
    
    # Deserialize from JSON
    restored_world_state = WorldState.from_json(json_data)
    print(f"V Deserialized WorldState from JSON")
    
    # Compare
    assert restored_world_state.characters == world_state.characters
    assert restored_world_state.locations == world_state.locations
    assert restored_world_state.timeline == world_state.timeline
    assert restored_world_state.flags == world_state.flags
    assert restored_world_state.inventory == world_state.inventory
    
    print("V Serialization/deserialization test passed")
    
    return restored_world_state


def test_migration():
    """Test migration from old format."""
    print("\n=== Testing Migration ===")
    
    # Create mock story log (old format)
    story_log = [
        {"role": "system", "content": "You are a game master..."},
        {"role": "user", "content": "I want to explore the forest"},
        {"role": "assistant", "content": "You enter a dark forest. The trees whisper secrets. Choose: 1) Follow the path 2) Climb a tree 3) Listen to whispers 4) Turn back"},
        {"role": "user", "content": "I choose to follow the path"},
        {"role": "assistant", "content": "The path leads to a clearing where you see a mysterious figure. Choose: 1) Approach 2) Hide 3) Call out 4) Circle around"}
    ]
    
    migration_service = MigrationService()
    
    # Test migration
    world_state = migration_service.migrate_from_story_log(story_log, "Aiden")
    
    print(f"V Migrated story log to WorldState")
    print(f"V Character count: {len(world_state.characters)}")
    print(f"V Location count: {len(world_state.locations)}")
    print(f"V Event count: {len(world_state.timeline)}")
    
    # Validate
    is_valid = migration_service.validate_world_state(world_state)
    print(f"V Validation result: {is_valid}")
    
    return world_state


def test_world_summary():
    """Test world summary generation."""
    print("\n=== Testing World Summary ===")
    
    migration_service = MigrationService()
    world_state = migration_service.create_empty_world_state("Test Hero")
    
    summary = world_state.get_world_summary()
    print(f"V World Summary: {summary}")
    
    return summary


def main():
    """Run all tests."""
    print("Starting WorldState tests...\n")
    
    try:
        # Test 1: Creation
        world_state = test_world_state_creation()
        
        # Test 2: Serialization
        restored_world_state = test_serialization(world_state)
        
        # Test 3: Migration
        migrated_world_state = test_migration()
        
        # Test 4: Summary
        summary = test_world_summary()
        
        print("\n=== All Tests Passed! ===")
        print("WorldState implementation is working correctly.")
        
        # Show example JSON output
        print("\n=== Example JSON Output ===")
        print(migrated_world_state.to_json())
        
    except Exception as e:
        print(f"\nX Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
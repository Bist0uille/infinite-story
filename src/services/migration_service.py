"""
Migration Service for RPBOT_v5.1

This module handles the migration from the old journal-based system
to the new structured WorldState format.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.world_state import WorldState, Character, Location, Event


class MigrationService:
    """Service for migrating from old data format to WorldState."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def migrate_from_story_log(self, story_log: List[Dict[str, Any]], 
                              hero_name: str = "Hero") -> WorldState:
        """
        Migrate from old story_log format to WorldState.
        
        Args:
            story_log: List of messages from the old system
            hero_name: Name of the main character
            
        Returns:
            WorldState: New world state object
        """
        world_state = WorldState()
        
        # Create the main character
        main_character = Character(
            id="main_character",
            name=hero_name,
            traits=["protagonist"],
            status="alive",
            location_id="current_location",
            arcs=["main_story"]
        )
        world_state.add_character(main_character)
        
        # Create initial location
        initial_location = Location(
            id="current_location",
            name="Starting Location",
            tags=["unknown"],
            description="The place where the adventure begins"
        )
        world_state.add_location(initial_location)
        
        # Process story log to extract events
        turn_number = 0
        for message in story_log:
            if message.get("role") == "assistant":
                turn_number += 1
                event = Event(
                    id=f"turn_{turn_number}",
                    descr=self._extract_event_description(message.get("content", "")),
                    ts=turn_number,
                    impact={"turn": turn_number}
                )
                world_state.add_event(event)
        
        self.logger.info(f"Migrated story log with {len(story_log)} messages to WorldState")
        return world_state
    
    def _extract_event_description(self, content: str) -> str:
        """Extract a brief description from story content."""
        # Take first sentence or first 100 characters
        lines = content.split('\n')
        first_line = lines[0] if lines else content
        
        # Extract first sentence
        sentences = first_line.split('.')
        if sentences:
            return sentences[0].strip()[:100]
        return content[:100]
    
    def migrate_from_save_file(self, save_data: Dict[str, Any]) -> WorldState:
        """
        Migrate from old save file format to WorldState.
        
        Args:
            save_data: Dictionary containing save game data
            
        Returns:
            WorldState: New world state object
        """
        world_state = WorldState()
        
        # Extract basic info
        hero_name = save_data.get("hero_name", "Hero")
        story_log = save_data.get("story_log", [])
        
        # Create main character
        main_character = Character(
            id="main_character",
            name=hero_name,
            traits=["protagonist"],
            status="alive",
            location_id="current_location",
            arcs=["main_story"]
        )
        world_state.add_character(main_character)
        
        # Create initial location
        initial_location = Location(
            id="current_location",
            name="Current Location",
            tags=["current"],
            description="The current location in the adventure"
        )
        world_state.add_location(initial_location)
        
        # Process story log
        turn_number = 0
        for message in story_log:
            if message.get("role") == "assistant":
                turn_number += 1
                event = Event(
                    id=f"save_turn_{turn_number}",
                    descr=self._extract_event_description(message.get("content", "")),
                    ts=turn_number,
                    impact={"turn": turn_number, "source": "save_file"}
                )
                world_state.add_event(event)
        
        # Set chapter based on number of turns
        if turn_number > 20:
            world_state.chapter = 3
        elif turn_number > 10:
            world_state.chapter = 2
        else:
            world_state.chapter = 1
        
        self.logger.info(f"Migrated save file to WorldState with {turn_number} turns")
        return world_state
    
    def create_empty_world_state(self, hero_name: str = "Hero") -> WorldState:
        """
        Create a new empty world state for a fresh game.
        
        Args:
            hero_name: Name of the main character
            
        Returns:
            WorldState: New empty world state
        """
        world_state = WorldState()
        
        # Create the main character
        main_character = Character(
            id="main_character",
            name=hero_name,
            traits=["protagonist"],
            status="alive",
            location_id="starting_location",
            arcs=["main_story"]
        )
        world_state.add_character(main_character)
        
        # Create starting location
        starting_location = Location(
            id="starting_location",
            name="Unknown Location",
            tags=["starting", "unknown"],
            description="The place where the adventure begins"
        )
        world_state.add_location(starting_location)
        
        # Add initial event
        initial_event = Event(
            id="game_start",
            descr="The adventure begins",
            ts=0,
            impact={"type": "game_start"}
        )
        world_state.add_event(initial_event)
        
        self.logger.info(f"Created empty world state for {hero_name}")
        return world_state
    
    def validate_world_state(self, world_state: WorldState) -> bool:
        """
        Validate that a world state is properly structured.
        
        Args:
            world_state: WorldState to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check that main character exists
            if "main_character" not in world_state.characters:
                self.logger.error("Main character not found in world state")
                return False
            
            # Check that all characters have valid locations
            for char_id, character in world_state.characters.items():
                if character.location_id not in world_state.locations:
                    self.logger.error(f"Character {char_id} has invalid location {character.location_id}")
                    return False
            
            # Check that timeline is ordered
            if world_state.timeline:
                timestamps = [event.ts for event in world_state.timeline]
                if timestamps != sorted(timestamps):
                    self.logger.warning("Timeline is not ordered by timestamp")
            
            self.logger.info("World state validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"World state validation failed: {e}")
            return False
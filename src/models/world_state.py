"""
World State Data Models for RPBOT_v5.1

This module defines the core data structures for maintaining game state:
- Characters (PNJ and player)
- Locations and environments
- Events and timeline
- World state container

Uses Pydantic for data validation and serialization.
"""

from typing import Any, Dict, List, Set, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Character(BaseModel):
    """
    Represents a character in the game world.
    
    Attributes:
        id: Unique identifier for the character
        name: Character's name
        traits: List of character traits/attributes
        status: Current status (alive, dead, missing, etc.)
        location_id: ID of current location
        arcs: List of story arcs this character is involved in
    """
    id: str = Field(..., description="Unique character identifier")
    name: str = Field(..., description="Character name")
    traits: List[str] = Field(default_factory=list, description="Character traits and attributes")
    status: str = Field(default="alive", description="Current character status")
    location_id: str = Field(..., description="Current location ID")
    arcs: List[str] = Field(default_factory=list, description="Story arcs involving this character")


class Location(BaseModel):
    """
    Represents a location in the game world.
    
    Attributes:
        id: Unique identifier for the location
        name: Location name
        tags: List of descriptive tags
        description: Brief description of the location
    """
    id: str = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Location name")
    tags: List[str] = Field(default_factory=list, description="Location tags")
    description: str = Field(..., description="Location description")


class Event(BaseModel):
    """
    Represents an event in the game timeline.
    
    Attributes:
        id: Unique identifier for the event
        descr: Event description
        ts: Timestamp (turn number or datetime)
        impact: Dictionary describing the event's impact on the world
        raw_response: The full, unprocessed response from the AI
    """
    id: str = Field(..., description="Unique event identifier")
    descr: str = Field(..., description="Event description")
    ts: int = Field(..., description="Event timestamp (turn number)")
    impact: Dict[str, Any] = Field(default_factory=dict, description="Event impact on world state")
    raw_response: Optional[str] = Field(default=None, description="The full, unprocessed response from the AI")


class WorldState(BaseModel):
    """
    Main container for the entire game world state.
    
    This is the central data structure that holds all game information:
    - Current chapter progression
    - All characters and their states
    - All locations and their properties
    - Player inventory
    - Game flags and conditions
    - Complete timeline of events
    """
    chapter: int = Field(default=1, description="Current chapter number")
    characters: Dict[str, Character] = Field(default_factory=dict, description="All characters in the world")
    locations: Dict[str, Location] = Field(default_factory=dict, description="All locations in the world")
    inventory: Set[str] = Field(default_factory=set, description="Player inventory items")
    flags: Dict[str, bool] = Field(default_factory=dict, description="Game state flags")
    timeline: List[Event] = Field(default_factory=list, description="Complete event timeline")
    
    def add_character(self, character: Character) -> None:
        """Add a character to the world state."""
        self.characters[character.id] = character
    
    def add_location(self, location: Location) -> None:
        """Add a location to the world state."""
        self.locations[location.id] = location
    
    def add_event(self, event: Event) -> None:
        """Add an event to the timeline."""
        self.timeline.append(event)
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get a character by ID."""
        return self.characters.get(character_id)
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        return self.locations.get(location_id)
    
    def get_characters_in_location(self, location_id: str) -> List[Character]:
        """Get all characters currently in a specific location."""
        return [char for char in self.characters.values() if char.location_id == location_id]
    
    def set_flag(self, flag_name: str, value: bool) -> None:
        """Set a game flag."""
        self.flags[flag_name] = value
    
    def get_flag(self, flag_name: str) -> bool:
        """Get a game flag value."""
        return self.flags.get(flag_name, False)
    
    def add_to_inventory(self, item: str) -> None:
        """Add an item to the player inventory."""
        self.inventory.add(item)
    
    def remove_from_inventory(self, item: str) -> None:
        """Remove an item from the player inventory."""
        self.inventory.discard(item)
    
    def has_item(self, item: str) -> bool:
        """Check if player has an item in inventory."""
        return item in self.inventory
    
    def get_recent_events(self, count: int = 5) -> List[Event]:
        """Get the most recent events from the timeline."""
        return self.timeline[-count:] if self.timeline else []
    
    def to_json(self) -> str:
        """Serialize the world state to JSON."""
        return self.model_dump_json(indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorldState':
        """Deserialize world state from JSON."""
        return cls.model_validate_json(json_str)
    
    def get_world_summary(self, exclude_defaults: bool = False) -> Dict[str, Any]:
        """
        Get a concise summary of the current world state for AI context.
        
        Args:
            exclude_defaults: If True, excludes empty lists or default values.
        """
        summary = {
            "chapter": self.chapter,
            "known_characters": [char.name for char_id, char in self.characters.items() if char_id != "main_character"],
            "known_locations": [loc.name for loc_id, loc in self.locations.items() if loc_id != "starting_location"],
            "inventory": list(self.inventory),
            "active_flags": [flag for flag, value in self.flags.items() if value],
            "timeline_length": len(self.timeline)
        }
        
        if exclude_defaults:
            # Filter out keys with empty or default values
            return {k: v for k, v in summary.items() if v and (k != "chapter" or v > 1)}
            
        return summary
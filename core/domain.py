from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class Character:
    """
    Flexible data container for character information.
    Driven by configuration - does not enforce a strict schema.
    """
    
    # Single values (Name, Race, HP, generic stats)
    # Key = Parameter Key (from config), Value = Extracted String/Int
    data_points: Dict[str, Any] = field(default_factory=dict)
    
    # List values (Classes, Skills, Inventory, Spells)
    # Key = List Name (from config), Value = List of dictionaries representing items
    # e.g., "Inventory": [
    #   {"Item": "Backpack", "Count": 1, "Weight": 5, ...},
    #   ...
    # ]
    lists: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    def add_data_point(self, key: str, value: Any):
        self.data_points[key] = value
        
    def add_list(self, key: str, items: List[Dict[str, Any]]):
        self.lists[key] = items

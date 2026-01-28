from abc import ABC, abstractmethod
from core.domain import Character

class EnricherStrategy(ABC):
    """
    Interface/Protocol for all Logic Enrichers.
    Ensures that main.py can treat any system (D&D, Pathfinder, etc.) identically.
    """
    
    @abstractmethod
    def enrich(self, character: Character) -> Character:
        """
        Derive new data points from the existing character data.
        Must return the modified character object.
        """
        pass

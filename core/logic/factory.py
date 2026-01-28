import logging
from core.logic.base import EnricherStrategy
from core.logic.dnd5e import DnD5eEnricher

logger = logging.getLogger("LogicFactory")

class NoOpEnricher(EnricherStrategy):
    """
    Null Object implementation. Does nothing.
    Used when no specific system logic is selected.
    """
    def enrich(self, character):
        logger.debug("NoOp Enricher: Passing data through untouched.")
        return character

class EnricherFactory:
    """
    Factory to instantiate the correct EnricherStrategy based on a string key.
    Future-proofs the app for GUI selection.
    """
    _registry = {
        "dnd5e": DnD5eEnricher,
        "none": NoOpEnricher
    }

    @classmethod
    def get(cls, name: str) -> EnricherStrategy:
        key = name.lower() if name else "none"
        enricher_class = cls._registry.get(key, NoOpEnricher)
        logger.info(f"Selected Logic Module: {key} ({enricher_class.__name__})")
        return enricher_class()

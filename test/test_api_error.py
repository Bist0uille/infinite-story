
import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.engine import GameEngine
from services.ai_service import AIClient
from utils.logger_config import setup_logging

async def main():
    """
    Tests the _extract_entities_from_narrative method in GameEngine
    to debug the 500 API error.
    """
    setup_logging()
    logging.info("--- Starting API Error Test ---")

    try:
        ai_client = AIClient()
        game_engine = GameEngine(ai_client)

        narrative_example = (
            "Vous arrivez dans le village de Bois-Tranquille. "
            "Une vieille femme nommée Elara la guérisseuse vous salue. "
            "Au loin, vous apercevez la Forêt Sombre."
        )

        logging.info(f"Attempting to extract entities from: '{narrative_example}'")
        
        # We call the internal method directly for this test
        entities = await game_engine._extract_entities_from_narrative(narrative_example)

        if entities:
            logging.info(f"SUCCESS: Extracted entities: {entities}")
        else:
            logging.error("FAILURE: No entities were extracted.")

    except Exception as e:
        logging.critical(f"An exception occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())

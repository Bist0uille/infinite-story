
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.engine import GameEngine
from services.ai_service import AIClient
from utils.logger_config import setup_logging

async def main():
    setup_logging()
    logging.getLogger().setLevel(logging.DEBUG) # Set root logger to DEBUG
    logging.info("--- Starting Full Flow API Test ---")

    try:
        ai_client = AIClient()
        game_engine = GameEngine(ai_client)
        game_engine.set_hero_name("Zane")

        # 1. Generate a story narrative
        logging.info("STEP 1: Generating story narrative...")
        story_prompt_messages = [
            {"role": "system", "content": "Aventure fantasy avec Zane. Style direct. Histoire courte + 4 choix."},
            {"role": "user", "content": "Commence l'aventure."}
        ]
        narrative_response = await ai_client.complete(story_prompt_messages, purpose="story_generation")
        
        if not narrative_response:
            logging.error("FAILURE: Did not receive a narrative response. Aborting test.")
            return

        narrative, _ = game_engine.extract_choices(narrative_response)
        logging.info(f"Generated Narrative: '{narrative}'")

        # 2. Extract entities from the generated narrative
        logging.info("STEP 2: Extracting entities from the narrative...")
        entities = await game_engine._extract_entities_from_narrative(narrative)

        if entities:
            logging.info(f"SUCCESS: Extracted entities: {entities}")
        else:
            logging.error("FAILURE: No entities were extracted.")

    except Exception as e:
        logging.critical(f"An exception occurred during the full flow test: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())

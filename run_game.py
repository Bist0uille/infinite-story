import asyncio
import logging
from src.gui_app import RPGApp
from src.logger_config import setup_logging

if __name__ == "__main__":
    setup_logging()  # Initialize logging
    try:
        app = RPGApp()
        asyncio.run(app.run())
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}", exc_info=True)
        # In a real app, you might want to log this to a file.
        input("Press Enter to exit...")


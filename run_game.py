"""
INFINITE STORY - Main Entry Point

A text-based RPG adventure game with AI-powered storytelling.
Modular architecture with clean separation of concerns.
"""
import asyncio
import logging
import sys
import os

# Add src to path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


from src.ui.main_window import RPGApp
from src.utils.logger_config import setup_logging


def main():
    """Main application entry point."""
    setup_logging()
    logging.info("Starting INFINITE STORY application...")
    
    try:
        app = RPGApp()
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}", exc_info=True)
        input("Press Enter to exit...")
    finally:
        logging.info("Application shutdown complete.")


if __name__ == "__main__":
    main()

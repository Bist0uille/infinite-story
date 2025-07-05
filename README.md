# 🚀 Infinite Story 🚀

Welcome to **Infinite Story**, a text-based RPG where your imagination is the only limit! This game uses the power of AI to generate a dynamic and ever-evolving narrative based on your choices.

![Screenshot](https://i.imgur.com/your-screenshot.png)  <!-- Replace with a real screenshot URL -->

## ✨ Features

*   **Dynamic Storytelling:** The AI crafts a unique story for every playthrough, ensuring no two adventures are the same.
*   **Choice-Driven Narrative:** Your decisions directly impact the story's direction, leading to unforeseen consequences and unique outcomes.
*   **Customizable Universes:** Create your own worlds with custom prompts or use one of the built-in presets to kickstart your adventure.
*   **Narrative Styles:** Define the tone of your story, from a classic adventure to a poetic saga or a humorous tale.
*   **Save/Load System:** Save your progress at any time and continue your adventure later.

## 🛠️ How to Play

1.  **Installation:**
    *   Clone the repository:
        ```bash
        git clone https://github.com/Bist0uille/infinite-story.git
        ```
    *   Navigate to the project directory:
        ```bash
        cd infinite-story
        ```
    *   Install the dependencies:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Configuration:**
    *   Create a `.env` file in the root directory of the project.
    *   Add your Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY=your_api_key
        ```

3.  **Run the game:**
    *   Execute the main script:
        ```bash
        python run_game.py
        ```

## 📂 Project Structure

The project is organized into the following components:

*   `run_game.py`: The main entry point of the application.
*   `src/`: Contains the core application logic.
    *   `ai_client.py`: Manages the interaction with the Gemini API.
    *   `data_manager.py`: Handles loading and saving of presets, custom data, and game saves.
    *   `gui_app.py`: Implements the graphical user interface using `customtkinter`.
    *   `logger_config.py`: Configures the application's logging.
*   `saves/`: Stores your saved game files.
*   `custom_universes.json`: Your custom-defined universes.
*   `custom_styles.json`: Your custom-defined narrative styles.
*   `preset_universes.json`: Pre-defined universes to get you started.
*   `preset_styles.json`: Pre-defined narrative styles.

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
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

The project follows a modular architecture with clean separation of concerns:

```
├── src/
│   ├── core/                 # Core game logic (UI-independent)
│   │   └── engine.py         # GameEngine - manages story state and game logic
│   ├── services/             # External service integrations
│   │   ├── ai_service.py     # AI API client (Gemini integration)
│   │   └── data_service.py   # Data persistence and file management
│   ├── ui/                   # User interface layer
│   │   └── main_window.py    # Main application window and UI logic
│   └── utils/                # Utility modules
│       └── logger_config.py  # Logging configuration
├── run_game.py              # Application entry point
├── saves/                   # Game save files directory
├── requirements.txt         # Python dependencies
└── Configuration files:
    ├── custom_universes.json    # User-defined story universes
    ├── custom_styles.json       # User-defined narrative styles
    ├── preset_universes.json    # Built-in story universes
    └── preset_styles.json       # Built-in narrative styles
```

### Architecture Benefits:
- **Modular Design:** Clear separation between game logic, UI, and services
- **Maintainability:** Each module has a single responsibility
- **Testability:** Core logic is independent of UI framework
- **Extensibility:** Easy to add new features or replace components

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
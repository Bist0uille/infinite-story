# 🚀 Infinite Story v5.1 🚀

Welcome to **Infinite Story**, a text-based RPG where your imagination is the only limit! This game uses the power of **Gemini 2.5-flash AI** to generate a dynamic and ever-evolving narrative based on your choices.

![Screenshot](https://i.imgur.com/your-screenshot.png)  <!-- Replace with a real screenshot URL -->

## ✨ Features

### 🎮 **Core Gameplay**
*   **Dynamic Storytelling:** The AI crafts a unique story for every playthrough, ensuring no two adventures are the same.
*   **Choice-Driven Narrative:** Your decisions directly impact the story's direction, leading to unforeseen consequences and unique outcomes.
*   **Customizable Universes:** Create your own worlds with custom prompts or use one of the built-in presets to kickstart your adventure.
*   **Narrative Styles:** Define the tone of your story, from a classic adventure to a poetic saga or a humorous tale.

### 🧠 **Advanced AI Integration**
*   **Smart World State:** Rich data model that tracks characters, locations, events, and relationships
*   **Automatic Entity Extraction:** AI automatically detects and tracks NPCs and locations from the narrative
*   **Contextual Memory:** The AI maintains consistency using structured world information instead of raw text
*   **Real-time World Updates:** See characters, locations, and story status update live as you play

### 📊 **Analytics & Performance**
*   **Token Usage Tracking:** Automatic monitoring of AI API consumption with detailed breakdowns
*   **Session Analytics:** Complete summary of tokens used, costs, and performance metrics
*   **Smart Context Management:** Optimized prompt handling for efficient token usage

### 💾 **Technical Features**
*   **Save/Load System:** Save your progress at any time and continue your adventure later
*   **Modular Architecture:** Clean separation between game logic, AI services, and UI
*   **Robust Error Handling:** Advanced retry mechanisms and graceful error recovery

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
        GEMINI_API_KEY=your_api_key_here
        ```
    *   Get your API key from [Google AI Studio](https://aistudio.google.com/)

3.  **Run the game:**
    *   Execute the main script:
        ```bash
        python3 run_game.py
        ```

4.  **Gameplay:**
    *   Choose your character name and select a universe (Fantasy, Sci-Fi, or create custom)
    *   Pick a narrative style to set the tone
    *   Make choices and watch your story unfold
    *   Monitor the world state panel to see NPCs and locations discovered
    *   Check logs for detailed token usage analytics

## 📂 Project Structure

The project follows a modular architecture with clean separation of concerns:

```
├── src/                          # Source code
│   ├── models/                   # Data models
│   │   ├── __init__.py           # Package initialization
│   │   └── world_state.py        # WorldState, Character, Location, Event models
│   ├── core/                     # Core game logic
│   │   └── engine.py             # GameEngine with entity extraction
│   ├── services/                 # External service integrations
│   │   ├── ai_service.py         # AI API client with token tracking
│   │   ├── data_service.py       # Data persistence and file management
│   │   └── migration_service.py  # Legacy data migration
│   ├── ui/                       # User interface layer
│   │   └── main_window.py        # Main application with world state display
│   └── utils/                    # Utility modules
│       └── logger_config.py      # Logging configuration
├── test/                         # Test files and diagnostics
├── saves/                        # Game save files directory
├── logs/                         # Application logs with token analytics
├── run_game.py                   # Application entry point
├── requirements.txt              # Python dependencies (includes pydantic)
└── Configuration files:
    ├── custom_universes.json     # User-defined story universes
    ├── custom_styles.json        # User-defined narrative styles
    ├── preset_universes.json     # Built-in story universes
    └── preset_styles.json        # Built-in narrative styles
```

### Architecture Benefits:
- **Modular Design:** Clear separation between game logic, UI, and services
- **Rich Data Model:** Pydantic-based WorldState for structured game data
- **Smart AI Integration:** Context-aware prompts with automatic entity extraction  
- **Performance Monitoring:** Built-in token usage tracking and cost estimation
- **Maintainability:** Each module has a single responsibility
- **Testability:** Core logic is independent of UI framework
- **Extensibility:** Easy to add new features or replace components

## 🔧 New in v5.1

### **WorldState System**
- **Rich Data Models:** Track characters, locations, events, and relationships
- **Automatic Entity Extraction:** AI detects NPCs and locations from narratives
- **Real-time Updates:** Live world state display in the UI
- **Legacy Migration:** Automatic conversion from old save formats

### **Token Analytics**
- **Usage Tracking:** Monitor API calls and token consumption
- **Cost Estimation:** Real-time cost calculations for Gemini API
- **Session Reports:** Detailed analytics logged at session end
- **Purpose Breakdown:** Track tokens by operation type (story, extraction, etc.)

### **Enhanced AI Integration**
- **Gemini 2.5-flash:** Latest model with improved performance
- **Context Optimization:** Smart prompt engineering for better consistency
- **Robust Error Handling:** Advanced retry mechanisms with exponential backoff
- **World-Aware Prompts:** AI receives structured context instead of raw text

## 📊 Token Usage Analytics

The game automatically tracks your API usage and provides detailed analytics:

```
🎯 SESSION TOKEN USAGE SUMMARY
============================================================
📅 Session Duration: 0:15:32
🔢 Total API Calls: 12
📥 Total Input Tokens: 8,456
📤 Total Output Tokens: 3,124  
🧠 Thoughts Tokens: 2,890
💯 TOTAL TOKENS: 14,470

📊 Breakdown by Purpose:
----------------------------------------
  STORY_GENERATION:
    Calls: 8
    Input: 6,234 tokens
    Output: 2,678 tokens
    Total: 8,912 tokens

  ENTITY_EXTRACTION:
    Calls: 4
    Input: 2,222 tokens
    Output: 446 tokens
    Total: 2,668 tokens

💰 Estimated Cost (Gemini 2.5-flash):
    Input: $0.0011
    Output: $0.0012
    TOTAL: $0.0023
============================================================
```

## 🤝 Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
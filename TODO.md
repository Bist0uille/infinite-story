# 🏗️ Plan d'Architecture Modulaire - INFINITE STORY

## 📊 Analyse du Code Actuel

### État Actuel
- **Total** : 864 lignes de code
- **gui_app.py** : 704 lignes (81% du code) - **MONOLITHIQUE**
- **Responsabilités mélangées** dans une seule classe

### Problèmes Identifiés
```python
class RPGApp(AsyncioTk):  # 704 lignes !
    # UI Construction (lignes 76-223)
    # Game Logic (lignes 272-631) 
    # Data Management (lignes 333-702)
    # AI Communication (lignes 425-507)
    # Event Handling (lignes 231-270)
```

### Responsabilités Mélangées
1. **Interface** : Widgets, layouts, events
2. **Logique Jeu** : story_log, world_state, choices
3. **Données** : univers, styles, sauvegardes
4. **IA** : communication, retry logic
5. **État** : font_size, game state, AI availability

---

## 🏗️ Architecture Modulaire Proposée

### 📁 Nouvelle Structure
```
src/
├── core/                    # Logique métier pure
│   ├── __init__.py
│   ├── game_engine.py       # Moteur principal (150 lignes)
│   ├── story_manager.py     # Gestion story_log + world_state (100 lignes)
│   └── choice_processor.py  # Traitement des choix (80 lignes)
│
├── services/                # Services externes
│   ├── __init__.py
│   ├── ai_service.py        # Service IA amélioré (120 lignes)
│   ├── data_service.py      # Gestion données (100 lignes)
│   └── save_service.py      # Sauvegardes (80 lignes)
│
├── ui/                      # Interface pure
│   ├── __init__.py
│   ├── main_window.py       # Fenêtre principale (200 lignes)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── story_display.py # Affichage récit (60 lignes)
│   │   ├── choice_panel.py  # Panneau choix (80 lignes)
│   │   └── control_tabs.py  # Onglets contrôle (120 lignes)
│
└── utils/                   # Utilitaires
    ├── __init__.py
    ├── events.py            # Système événements (60 lignes)
    └── config.py            # Configuration (40 lignes)
```

### 🔧 Composants Principaux

#### 1. **Game Engine** (`core/game_engine.py`)
```python
class GameEngine:
    def __init__(self, ai_service, data_service, save_service):
        self.story_manager = StoryManager()
        self.choice_processor = ChoiceProcessor()
        # Injection de dépendances
        
    async def start_new_game(self, hero_name, universe, style):
        """Lance nouvelle partie"""
        
    async def process_player_choice(self, choice_text):
        """Traite choix joueur"""
        
    def get_current_state(self):
        """Retourne état actuel"""
```

#### 2. **Story Manager** (`core/story_manager.py`)
```python
class StoryManager:
    def __init__(self):
        self.story_log = []
        self.world_state = {}
        
    def add_message(self, role, content):
        """Ajoute message au log"""
        
    def update_world_facts(self, facts):
        """Met à jour les faits du monde"""
        
    def build_context_prompt(self, user_input):
        """Construit prompt avec contexte"""
```

#### 3. **UI Components** (`ui/main_window.py`)
```python
class MainWindow(ctk.CTk):
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.story_display = StoryDisplay()
        self.choice_panel = ChoicePanel()
        self.control_tabs = ControlTabs()
        
    def update_story(self, text):
        """Met à jour affichage histoire"""
        
    def update_choices(self, choices):
        """Met à jour boutons choix"""
```

#### 4. **Event System** (`utils/events.py`)
```python
class EventBus:
    def emit(self, event_type, data):
        """Émet événement"""
        
    def subscribe(self, event_type, callback):
        """S'abonne à événement"""

# Événements :
# - story_updated
# - choices_available  
# - game_started
# - ai_error
```

---

## 📋 TODO List d'Implémentation

### PHASE 1 : Core Logic (3-4h)
- [ ] **P1.1** : Créer la structure des dossiers
- [ ] **P1.2** : Extraire StoryManager de gui_app.py
- [ ] **P1.3** : Extraire ChoiceProcessor de gui_app.py  
- [ ] **P1.4** : Créer GameEngine avec injection dépendances

### PHASE 2 : Services (2-3h)
- [ ] **P2.1** : Créer le système d'événements EventBus
- [ ] **P2.2** : Améliorer ai_client.py en AIService
- [ ] **P2.3** : Extraire DataService de data_manager.py
- [ ] **P2.4** : Créer SaveService pour sauvegardes

### PHASE 3 : UI Components (3-4h)
- [ ] **P3.1** : Décomposer gui_app.py en composants UI
- [ ] **P3.2** : Créer StoryDisplay component
- [ ] **P3.3** : Créer ChoicePanel component
- [ ] **P3.4** : Créer ControlTabs component

### PHASE 4 : Integration & Tests (1-2h)
- [ ] **P4.1** : Connecter GameEngine avec EventBus
- [ ] **P4.2** : Connecter UI components avec EventBus
- [ ] **P4.3** : Tester et déboguer l'application modulaire
- [ ] **P4.4** : Nettoyer ancien code gui_app.py

---

## 🎯 Bénéfices de l'Architecture Modulaire

### ✅ Avantages Immédiats
- **Lisibilité** : Fichiers de 60-200 lignes vs 704 lignes
- **Testabilité** : Tests unitaires possibles sur chaque composant  
- **Maintenabilité** : Modifications isolées par responsabilité
- **Réutilisabilité** : Services réutilisables entre composants

### 🚀 Extensibilité Future
- **Plugins** : Nouveaux styles/univers par modules
- **Thèmes UI** : Interface modulaire facilement personnalisable
- **Multi-IA** : Support facile de plusieurs modèles IA
- **API REST** : GameEngine réutilisable pour interface web

---

## ⏱️ Estimation d'Implémentation

**PHASE 1** (3-4h) : Core Logic
- Extraction logique métier de gui_app.py
- Création GameEngine, StoryManager, ChoiceProcessor

**PHASE 2** (2-3h) : Services  
- EventBus, AIService amélioré, DataService, SaveService

**PHASE 3** (3-4h) : UI Components
- Décomposition interface en composants modulaires

**PHASE 4** (1-2h) : Integration & Tests
- Connexion EventBus, tests, nettoyage

**Total estimé : 9-13 heures**

---

## 🚨 Notes Importantes

### Migration Progressive
- L'application continuera de fonctionner à chaque étape
- Pas de régression de fonctionnalités
- Tests après chaque phase

### Responsabilités Claires
- **Core** : Logique métier pure, pas d'UI
- **Services** : Accès données, IA, sauvegardes  
- **UI** : Interface pure, pas de logique métier
- **Utils** : Événements, configuration

### Flux de Communication
```
User Action → UI → Event Bus → Game Engine → AI Service
                     ↓              ↓
              UI Update ← Event Bus ← Story State
```

---

## 🎯 Prochaine Session

1. **Commencer par PHASE 1** : Extraction logique métier
2. **Valider chaque étape** avant de continuer
3. **Tester régulièrement** que tout fonctionne
4. **Documenter** les changements au fur et à mesure

**Le plan est prêt pour l'implémentation !**
#!/usr/bin/env python3
"""
Tests de diagnostic pour identifier le problème exact avec l'API Gemini
"""

import sys
import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class APITester:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    async def test_minimal_request(self):
        """Test avec le prompt le plus minimal possible"""
        print("🧪 TEST 1: Prompt ultra-minimal")
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Hello"}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 50
            }
        }
        
        result = await self._make_request("gemini-2.5-flash", data)
        print(f"   Résultat: {result}")
        return result
    
    async def test_different_models(self):
        """Test avec différents modèles"""
        print("\n🧪 TEST 2: Différents modèles")
        
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
        
        for model in models:
            print(f"   Testing {model}...")
            data = {
                "contents": [
                    {
                        "role": "user", 
                        "parts": [{"text": "Write a short story."}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 100
                }
            }
            
            result = await self._make_request(model, data)
            print(f"   {model}: {result}")
    
    async def test_progressive_tokens(self):
        """Test avec des limites progressives de tokens"""
        print("\n🧪 TEST 3: Limites progressives de tokens")
        
        token_limits = [50, 100, 200, 400, 600, 800, 1024]
        
        for limit in token_limits:
            print(f"   Testing maxOutputTokens: {limit}")
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "Tell me a story about a hero."}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": limit
                }
            }
            
            result = await self._make_request("gemini-2.5-flash", data)
            print(f"   {limit} tokens: {result}")
            
            if "ERROR" not in result:
                break  # Trouver la limite qui marche
    
    async def test_our_exact_prompt(self):
        """Test avec notre prompt exact du jeu"""
        print("\n🧪 TEST 4: Notre prompt exact")
        
        # Simuler notre prompt système exact
        system_content = "Aventure fantasy avec Tim dans un monde médiéval. Style: tension et suspense. Format strict: histoire courte + 4 choix numérotés."
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": system_content}]
                },
                {
                    "role": "model", 
                    "parts": [{"text": "Compris, je vais créer une aventure fantasy."}]
                },
                {
                    "role": "user",
                    "parts": [{"text": "Choix du joueur: 'Commence l'aventure'. Histoire + 4 choix."}]
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 600
            }
        }
        
        result = await self._make_request("gemini-2.5-flash", data)
        print(f"   Notre prompt: {result}")
        
        # Test aussi avec moins de tokens
        data["generationConfig"]["maxOutputTokens"] = 300
        result2 = await self._make_request("gemini-2.5-flash", data)
        print(f"   Avec 300 tokens: {result2}")
    
    async def test_api_info(self):
        """Tester les infos sur notre API key / modèle"""
        print("\n🧪 TEST 5: Informations API")
        
        # Test de liste des modèles disponibles
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}",
                    headers={"x-goog-api-key": self.api_key}
                ) as response:
                    if response.status == 200:
                        models_info = await response.json()
                        print(f"   Modèles disponibles: {[m.get('name', 'unknown') for m in models_info.get('models', [])]}")
                    else:
                        print(f"   Erreur liste modèles: {response.status}")
        except Exception as e:
            print(f"   Erreur connexion: {e}")
    
    async def _make_request(self, model, data):
        """Faire une requête à l'API et retourner le résultat"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model}:generateContent",
                    headers=self.headers,
                    json=data,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        return f"ERROR {response.status}: {result}"
                    
                    # Vérifier la structure de réponse
                    if "candidates" not in result:
                        return f"ERROR: No candidates - {result}"
                    
                    candidate = result["candidates"][0]
                    finish_reason = candidate.get("finishReason", "UNKNOWN")
                    
                    if finish_reason == "MAX_TOKENS":
                        return f"MAX_TOKENS (expected: limit reached)"
                    elif finish_reason == "STOP":
                        content_length = len(candidate.get("content", {}).get("parts", [{}])[0].get("text", ""))
                        return f"SUCCESS ({content_length} chars)"
                    else:
                        return f"FINISH_REASON: {finish_reason}"
                        
        except asyncio.TimeoutError:
            return "ERROR: Timeout"
        except Exception as e:
            return f"ERROR: {str(e)}"

async def run_all_tests():
    """Exécuter tous les tests de diagnostic"""
    print("🔍 DIAGNOSTIC COMPLET DE L'API GEMINI")
    print("=" * 50)
    
    tester = APITester()
    
    if not tester.api_key:
        print("❌ ERREUR: Pas de clé API trouvée!")
        return
    
    print(f"✅ Clé API trouvée: {tester.api_key[:20]}...")
    
    # Exécuter tous les tests
    await tester.test_minimal_request()
    await tester.test_different_models()
    await tester.test_progressive_tokens()
    await tester.test_our_exact_prompt()
    await tester.test_api_info()
    
    print("\n🎯 CONCLUSIONS:")
    print("   - Si TOUS les tests échouent → Problème clé API ou quota")
    print("   - Si certains modèles marchent → Problème spécifique gemini-2.5-flash")
    print("   - Si limites basses marchent → Problème de taille de contexte")
    print("   - Si prompt simple marche → Problème avec notre structure")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
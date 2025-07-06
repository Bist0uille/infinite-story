#!/usr/bin/env python3
"""
Test simple de l'API Gemini sans dépendances
"""

import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

def test_api_with_curl():
    """Test l'API avec curl"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERREUR: Pas de clé API trouvée!")
        return
    
    print("🔍 TEST API GEMINI AVEC CURL")
    print("=" * 40)
    print(f"✅ Clé API: {api_key[:20]}...")
    
    # Test 1: Minimal avec gemini-1.5-flash
    print("\n🧪 TEST 1: Minimal gemini-1.5-flash")
    test_minimal_1_5_flash(api_key)
    
    # Test 2: Minimal avec gemini-2.5-flash  
    print("\n🧪 TEST 2: Minimal gemini-2.5-flash")
    test_minimal_2_5_flash(api_key)
    
    # Test 3: Notre prompt exact
    print("\n🧪 TEST 3: Notre prompt exact")
    test_our_prompt(api_key)

def test_minimal_1_5_flash(api_key):
    """Test minimal avec gemini-1.5-flash"""
    payload = {
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
    
    result = make_curl_request(api_key, "gemini-1.5-flash", payload)
    print(f"   Résultat 1.5-flash: {result}")

def test_minimal_2_5_flash(api_key):
    """Test minimal avec gemini-2.5-flash"""
    payload = {
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
    
    result = make_curl_request(api_key, "gemini-2.5-flash", payload)
    print(f"   Résultat 2.5-flash: {result}")

def test_our_prompt(api_key):
    """Test avec notre prompt du jeu"""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Aventure fantasy avec Tim. Histoire + 4 choix."}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.8
        }
    }
    
    result = make_curl_request(api_key, "gemini-1.5-flash", payload)
    print(f"   Notre prompt avec 1.5-flash: {result}")

def make_curl_request(api_key, model, payload):
    """Faire un appel curl à l'API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    # Créer le fichier JSON temporaire
    with open("/tmp/payload.json", "w") as f:
        json.dump(payload, f)
    
    try:
        # Commande curl
        cmd = [
            "curl", "-s",
            "-H", f"x-goog-api-key: {api_key}",
            "-H", "Content-Type: application/json",
            "-d", f"@/tmp/payload.json",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return f"CURL_ERROR: {result.stderr}"
        
        # Parser la réponse JSON
        try:
            response = json.loads(result.stdout)
            
            if "error" in response:
                return f"API_ERROR: {response['error']}"
            
            if "candidates" not in response:
                return f"NO_CANDIDATES: {response}"
            
            candidate = response["candidates"][0]
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            
            if finish_reason == "MAX_TOKENS":
                return "MAX_TOKENS - même problème!"
            elif finish_reason == "STOP":
                text_length = len(candidate.get("content", {}).get("parts", [{}])[0].get("text", ""))
                return f"SUCCESS - {text_length} caractères générés"
            else:
                return f"FINISH_REASON: {finish_reason}"
                
        except json.JSONDecodeError as e:
            return f"JSON_ERROR: {result.stdout[:200]}"
        
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        # Nettoyer
        if os.path.exists("/tmp/payload.json"):
            os.remove("/tmp/payload.json")

if __name__ == "__main__":
    test_api_with_curl()
#!/bin/bash

# Test direct de l'API Gemini avec curl
echo "🔍 TEST DIRECT API GEMINI"
echo "=========================="

# Lire la clé API depuis .env
if [ -f ".env" ]; then
    API_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2)
else
    echo "❌ Fichier .env non trouvé!"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo "❌ Clé API non trouvée dans .env!"
    exit 1
fi

echo "✅ Clé API trouvée: ${API_KEY:0:20}..."

# Test 1: Minimal avec gemini-1.5-flash
echo ""
echo "🧪 TEST 1: Minimal gemini-1.5-flash (50 tokens)"
curl -s \
  -H "x-goog-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Hello"}]
      }
    ],
    "generationConfig": {
      "maxOutputTokens": 50
    }
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent" | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f'   ❌ ERREUR: {data[\"error\"]}')
    elif 'candidates' in data:
        reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
        if reason == 'STOP':
            text_len = len(data['candidates'][0]['content']['parts'][0]['text'])
            print(f'   ✅ SUCCESS: {text_len} caractères générés')
        else:
            print(f'   ⚠️  FINISH_REASON: {reason}')
    else:
        print(f'   ❌ RÉPONSE INATTENDUE: {data}')
except Exception as e:
    print(f'   ❌ ERREUR PARSING: {e}')
"

# Test 2: Minimal avec gemini-2.5-flash
echo ""
echo "🧪 TEST 2: Minimal gemini-2.5-flash (50 tokens)"
curl -s \
  -H "x-goog-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Hello"}]
      }
    ],
    "generationConfig": {
      "maxOutputTokens": 50
    }
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f'   ❌ ERREUR: {data[\"error\"]}')
    elif 'candidates' in data:
        reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
        if reason == 'STOP':
            text_len = len(data['candidates'][0]['content']['parts'][0]['text'])
            print(f'   ✅ SUCCESS: {text_len} caractères générés')
        else:
            print(f'   ⚠️  FINISH_REASON: {reason}')
    else:
        print(f'   ❌ RÉPONSE INATTENDUE: {data}')
except Exception as e:
    print(f'   ❌ ERREUR PARSING: {e}')
"

# Test 3: Notre prompt style RPG
echo ""
echo "🧪 TEST 3: Prompt RPG avec gemini-1.5-flash (300 tokens)"
curl -s \
  -H "x-goog-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Aventure fantasy avec Tim. Écris une histoire courte + 4 choix numérotés."}]
      }
    ],
    "generationConfig": {
      "maxOutputTokens": 300,
      "temperature": 0.8
    }
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent" | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f'   ❌ ERREUR: {data[\"error\"]}')
    elif 'candidates' in data:
        reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
        if reason == 'STOP':
            text_len = len(data['candidates'][0]['content']['parts'][0]['text'])
            print(f'   ✅ SUCCESS: {text_len} caractères générés')
            print(f'   📝 Début: {data[\"candidates\"][0][\"content\"][\"parts\"][0][\"text\"][:100]}...')
        else:
            print(f'   ⚠️  FINISH_REASON: {reason}')
    else:
        print(f'   ❌ RÉPONSE INATTENDUE: {data}')
except Exception as e:
    print(f'   ❌ ERREUR PARSING: {e}')
"

echo ""
echo "🎯 CONCLUSIONS:"
echo "   - Si TEST 1 marche → API OK, problème avec 2.5-flash"
echo "   - Si TEST 1 échoue → Problème clé API ou quota"
echo "   - Si TEST 3 marche → Notre code a un problème"
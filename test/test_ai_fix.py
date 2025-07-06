#!/usr/bin/env python3
"""
Test du fix AI avec simulation de différents cas d'erreur
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service_fixed import AIClient
from src.utils.logger_config import setup_logging
import logging

def test_extraction_method():
    """Test de la méthode d'extraction sur différents cas"""
    
    setup_logging()
    client = AIClient()
    
    print("🧪 TEST DE LA MÉTHODE D'EXTRACTION")
    print("="*50)
    
    # Cas 1: Réponse normale
    normal_response = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Voici une réponse normale"}]
            },
            "finishReason": "STOP"
        }]
    }
    
    content, status = client._extract_response_content(normal_response)
    print(f"✅ Réponse normale: '{content}' | Status: {status}")
    
    # Cas 2: Blocage SAFETY
    safety_blocked = {
        "candidates": [{
            "finishReason": "SAFETY"
        }]
    }
    
    content, status = client._extract_response_content(safety_blocked)
    print(f"🛡️ Blocage SAFETY: '{content}' | Status: {status}")
    
    # Cas 3: Pas de parts (notre bug)
    no_parts = {
        "candidates": [{
            "content": {},
            "finishReason": "STOP"
        }]
    }
    
    content, status = client._extract_response_content(no_parts)
    print(f"❌ Pas de parts: '{content}' | Status: {status}")
    
    # Cas 4: Pas de candidates
    no_candidates = {"candidates": []}
    
    content, status = client._extract_response_content(no_candidates)
    print(f"❌ Pas de candidates: '{content}' | Status: {status}")
    
    print("\n🎯 TOUS LES CAS GÉRÉS SANS CRASH!")

if __name__ == "__main__":
    test_extraction_method()
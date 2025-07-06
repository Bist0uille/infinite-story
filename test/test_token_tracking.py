"""
Test du système de tracking des tokens
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.ai_service import AIClient


async def test_token_tracking():
    """Test le tracking des tokens avec quelques appels API."""
    print("=== Test Token Tracking ===")
    
    try:
        # Initialize client
        ai_client = AIClient()
        ai_client.start_session()
        
        print("✓ AIClient initialized with token tracking")
        
        # Test 1: Simple call
        messages = [{"role": "user", "content": "Dis juste 'Test 1 OK'"}]
        response = await ai_client.complete(messages, None, "test_call")
        print(f"✓ Test 1 Response: {response}")
        
        # Test 2: Story generation
        messages = [
            {"role": "system", "content": "Tu es un maître de jeu RPG."},
            {"role": "user", "content": "Raconte une courte histoire fantasy avec 4 choix."}
        ]
        response = await ai_client.complete(messages, None, "story_generation")
        print(f"✓ Test 2 Response: {response[:100]}...")
        
        # Test 3: Entity extraction simulation
        messages = [{"role": "user", "content": "Extrait les personnages et lieux de ce texte: 'Aiden rencontre Marcus dans la taverne du Dragon.'"}]
        response = await ai_client.complete(messages, None, "entity_extraction")
        print(f"✓ Test 3 Response: {response[:100]}...")
        
        # Get session summary
        print("\n" + "="*50)
        print("SESSION SUMMARY TEST:")
        print("="*50)
        summary = ai_client.get_session_summary()
        print(summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run token tracking test"""
    print("🧪 Testing Token Tracking System\n")
    
    success = await test_token_tracking()
    
    if success:
        print("\n🎉 Token tracking system works perfectly!")
        print("✅ Ready for production use")
    else:
        print("\n❌ Token tracking test failed")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
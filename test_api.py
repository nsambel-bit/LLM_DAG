"""Quick test to verify API key works."""

from src.core.llm_client import get_llm_client

def test_api():
    """Test that the API key works."""
    print("="*70)
    print("Testing OpenRouter API Connection")
    print("="*70)
    
    try:
        # Initialize client
        print("\n[1/3] Initializing LLM client...")
        client = get_llm_client()
        print("  [OK] Client initialized")
        print(f"  Model: {client.model}")
        
        # Make a simple test call
        print("\n[2/3] Testing API call...")
        response = client.complete(
            prompt="Say 'API test successful' if you receive this message.",
            temperature=0.1,
            max_tokens=50
        )
        print("  [OK] API call successful")
        print(f"  Response: {response[:100]}...")
        
        # Verify response
        print("\n[3/3] Verifying response...")
        if response and len(response) > 0:
            print("  [OK] Response received")
            
            print("\n" + "="*70)
            print("[SUCCESS] API KEY IS WORKING!")
            print("="*70)
            print("\nYou're all set! Try running:")
            print("  python examples/basic_example.py")
            print("  python examples/health_example.py")
            print("="*70)
            return True
        else:
            print("  [WARN] Empty response received")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] API test failed: {e}")
        print("\nPossible issues:")
        print("  1. API key is invalid")
        print("  2. No credits in OpenRouter account")
        print("  3. Network connection issue")
        print("\nPlease check:")
        print("  - API key at: https://openrouter.ai/keys")
        print("  - Credits at: https://openrouter.ai/credits")
        return False

if __name__ == "__main__":
    test_api()


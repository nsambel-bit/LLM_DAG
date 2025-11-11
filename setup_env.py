"""Setup script to create .env file with API key."""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with the provided API key."""
    
    env_content = """# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# LLM Configuration
LLM_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096

# Discovery Configuration
CONFIDENCE_THRESHOLD=0.5
SIGNIFICANCE_LEVEL=0.05
N_SAMPLES=5
MAX_REFINEMENT_ITERATIONS=3
"""
    
    env_path = Path(".env")
    
    # Write the file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("[SUCCESS] .env file created!")
    print(f"Location: {env_path.absolute()}")
    print("\nAPI Key configured:")
    print("  OPENROUTER_API_KEY: sk-or-v1-...96be")
    print("  LLM_MODEL: anthropic/claude-3.5-sonnet")
    
    # Verify it works
    print("\nVerifying setup...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("LLM_MODEL")
    
    if api_key:
        print(f"  [OK] API key loaded: {api_key[:20]}...{api_key[-10:]}")
    if model:
        print(f"  [OK] Model loaded: {model}")
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nYou can now run:")
    print("  python examples/basic_example.py")
    print("  python examples/health_example.py")
    print("="*70)

if __name__ == "__main__":
    create_env_file()


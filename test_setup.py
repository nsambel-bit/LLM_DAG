"""Test that the setup is correct."""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.discovery import HybridCausalDiscovery
        print("  [OK] HybridCausalDiscovery")
        
        from src.models.data_structures import Variable, DiscoveryConfig
        print("  [OK] Variable, DiscoveryConfig")
        
        from src.core.llm_client import LLMClient
        print("  [OK] LLMClient")
        
        from src.core.causal_graph import CausalGraph
        print("  [OK] CausalGraph")
        
        from src.modules.knowledge_extractor import KnowledgeExtractor
        print("  [OK] KnowledgeExtractor")
        
        from src.modules.statistical_analyzer import StatisticalAnalyzer
        print("  [OK] StatisticalAnalyzer")
        
        from src.modules.graph_builder import ConfidentGraphBuilder
        print("  [OK] ConfidentGraphBuilder")
        
        from src.modules.conflict_resolver import ConflictResolver
        print("  [OK] ConflictResolver")
        
        from src.modules.graph_validator import GraphValidator
        print("  [OK] GraphValidator")
        
        print("\n[SUCCESS] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n[FAIL] Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("\nTesting basic functionality...")
    
    try:
        from src.models.data_structures import Variable, CausalEdge
        from src.core.causal_graph import CausalGraph
        
        # Create variables
        var1 = Variable(name="X", description="Test variable X")
        var2 = Variable(name="Y", description="Test variable Y")
        print("  [OK] Variables created")
        
        # Create graph
        graph = CausalGraph()
        graph.add_edge(var1, var2, confidence=0.8, mechanism="Test mechanism")
        print("  [OK] Graph created and edge added")
        
        # Check graph properties
        assert len(graph.edges) == 1
        assert graph.get_average_confidence() == 0.8
        print("  [OK] Graph properties verified")
        
        print("\n[SUCCESS] Basic functionality works!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_environment():
    """Check environment setup."""
    print("\nChecking environment...")
    
    import os
    from pathlib import Path
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("  [OK] .env file exists")
        
        # Check if API key is set
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key and api_key != "your_api_key_here":
            print("  [OK] OPENROUTER_API_KEY is set")
        else:
            print("  [WARN] OPENROUTER_API_KEY not configured (set in .env file)")
    else:
        print("  [WARN] .env file not found (copy config/.env.example to .env)")
    
    # Check directories
    if Path("src").exists():
        print("  [OK] src/ directory exists")
    if Path("tests").exists():
        print("  [OK] tests/ directory exists")
    if Path("examples").exists():
        print("  [OK] examples/ directory exists")
    
    print("\n[SUCCESS] Environment check complete!")


def main():
    """Run all tests."""
    print("="*70)
    print("SETUP VERIFICATION")
    print("="*70)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    # Check environment
    check_environment()
    
    print("\n" + "="*70)
    if success:
        print("[SUCCESS] SETUP COMPLETE - System is ready to use!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Set your OPENROUTER_API_KEY in .env file")
        print("  2. Run: python examples/basic_example.py")
        print("  3. Or run: python examples/health_example.py")
        sys.exit(0)
    else:
        print("[FAIL] SETUP INCOMPLETE - Please fix the errors above")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()


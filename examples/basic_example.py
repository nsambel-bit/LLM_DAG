"""Basic example of using the hybrid causal discovery system without data."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig
from src.core.llm_client import get_llm_client


def main():
    """Run basic causal discovery example."""
    
    print("="*70)
    print("Basic Causal Discovery Example (Knowledge-Based Only)")
    print("="*70)
    
    # Define variables with descriptions
    variables = [
        Variable(
            name='Smoking',
            description='Number of cigarettes smoked per day. A behavioral choice.'
        ),
        Variable(
            name='Exercise',
            description='Hours of physical exercise per week. A lifestyle factor.'
        ),
        Variable(
            name='BMI',
            description='Body Mass Index, a measure of body fat based on height and weight.'
        ),
        Variable(
            name='Blood_Pressure',
            description='Systolic blood pressure in mmHg, indicates cardiovascular health.'
        ),
        Variable(
            name='Diabetes',
            description='Presence of type 2 diabetes (binary: yes/no).'
        )
    ]
    
    print(f"\nVariables to analyze: {len(variables)}")
    for var in variables:
        print(f"  - {var.name}: {var.description}")
    
    # Initialize LLM client
    print("\nInitializing LLM client...")
    try:
        llm_client = get_llm_client()
        print("[OK] LLM client initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize LLM client: {e}")
        print("\nPlease ensure:")
        print("  1. You have set OPENROUTER_API_KEY in your .env file")
        print("  2. The API key is valid")
        return
    
    # Initialize discovery system
    print("\nInitializing discovery system...")
    discovery = HybridCausalDiscovery(llm_client=llm_client)
    
    # Configure discovery
    config = DiscoveryConfig(
        resolve_conflicts=False,  # No statistical data to conflict with
        iterative_refinement=True,
        max_refinement_iterations=2,
        n_samples=3  # Number of LLM samples for consistency
    )
    
    # Run discovery
    print("\nStarting causal discovery...")
    try:
        result = discovery.discover(
            variables=variables,
            data=None,  # No observational data
            config=config
        )
        
        # Print results
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        
        print(f"\nDiscovered Causal Graph:")
        print(f"  Variables: {len(result.graph.get_all_variables())}")
        print(f"  Edges: {len(result.graph.edges)}")
        print(f"  Root Causes: {len(result.graph.get_roots())}")
        print(f"  Average Confidence: {result.graph.get_average_confidence():.2f}")
        
        print(f"\nRoot Causes:")
        for root in result.graph.get_roots():
            reasoning = result.graph.root_reasoning.get(root, "N/A")
            print(f"  - {root.name}")
            print(f"    Reasoning: {reasoning[:100]}...")
        
        print(f"\nCausal Relationships:")
        for edge in sorted(result.graph.edges, key=lambda e: e.confidence, reverse=True):
            print(f"  {edge.source.name} -> {edge.target.name}")
            print(f"    Confidence: {edge.confidence:.2f}")
            print(f"    Mechanism: {edge.mechanism[:80]}...")
        
        print(f"\nValidation Status:")
        for test_name, result_obj in result.validation.tests.items():
            status = "[OK]" if result_obj.passed else "[FAIL]"
            print(f"  {status} {test_name}: score={result_obj.score:.2f}")
        
        # Generate explanation
        print("\n" + "="*70)
        print("GRAPH EXPLANATION")
        print("="*70)
        
        explanation = discovery.explain_graph(result.graph)
        print(f"\n{explanation}")
        
        # Save results
        print("\n" + "="*70)
        print("SAVING RESULTS")
        print("="*70)
        
        os.makedirs('outputs', exist_ok=True)
        
        # Save report
        result.report.save('outputs/basic_example_report.json')
        print("[OK] Report saved to outputs/basic_example_report.json")
        
        # Save visualization
        result.graph.visualize('outputs/basic_example_graph.png')
        print("[OK] Graph visualization saved to outputs/basic_example_graph.png")
        
        # Save graph structure
        import json
        with open('outputs/basic_example_graph.json', 'w') as f:
            json.dump(result.graph.to_dict(), f, indent=2)
        print("[OK] Graph structure saved to outputs/basic_example_graph.json")
        
    except Exception as e:
        print(f"\n[FAIL] Discovery failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


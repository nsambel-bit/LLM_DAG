"""Health domain example with synthetic data."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig
from src.core.llm_client import get_llm_client
from examples.generate_sample_data import generate_health_data


def main():
    """Run health domain causal discovery with data."""
    
    print("="*70)
    print("Health Domain Causal Discovery Example")
    print("="*70)
    
    # Generate synthetic data
    print("\nGenerating synthetic health data...")
    data = generate_health_data(n_samples=500)
    print(f"[OK] Generated {len(data)} samples")
    print(f"\nData columns: {list(data.columns)}")
    print(f"\nData preview:")
    print(data.head())
    print(f"\nData statistics:")
    print(data.describe())
    
    # Define variables with descriptions
    variables = [
        Variable(
            name='Smoking',
            description='Number of cigarettes smoked per day. A modifiable risk factor.'
        ),
        Variable(
            name='Exercise',
            description='Hours of physical exercise per week. A protective lifestyle factor.'
        ),
        Variable(
            name='BMI',
            description='Body Mass Index. A measure of body composition calculated from height and weight.'
        ),
        Variable(
            name='Blood_Pressure',
            description='Systolic blood pressure in mmHg. An indicator of cardiovascular health.'
        ),
        Variable(
            name='Diabetes',
            description='Presence of type 2 diabetes. A chronic metabolic disease (binary: 0/1).'
        )
    ]
    
    # Initialize LLM client
    print("\nInitializing LLM client...")
    try:
        llm_client = get_llm_client()
        print("[OK] LLM client initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize LLM client: {e}")
        print("\nPlease ensure OPENROUTER_API_KEY is set in your .env file")
        return
    
    # Initialize discovery system
    print("\nInitializing hybrid discovery system...")
    discovery = HybridCausalDiscovery(llm_client=llm_client)
    
    # Configure discovery with both knowledge and data
    config = DiscoveryConfig(
        resolve_conflicts=True,  # Use conflict resolution
        iterative_refinement=True,
        max_refinement_iterations=3,
        significance_level=0.05,
        confidence_threshold=0.5,
        n_samples=3
    )
    
    # Run discovery
    print("\nStarting hybrid causal discovery...")
    try:
        result = discovery.discover(
            variables=variables,
            data=data,
            config=config
        )
        
        # Print detailed results
        print("\n" + "="*70)
        print("DISCOVERY RESULTS")
        print("="*70)
        
        print(f"\nGraph Statistics:")
        print(f"  Variables: {len(result.graph.get_all_variables())}")
        print(f"  Edges: {len(result.graph.edges)}")
        print(f"  Root Causes: {len(result.graph.get_roots())}")
        print(f"  Average Confidence: {result.graph.get_average_confidence():.2f}")
        print(f"  Deferred Edges: {len(result.graph.deferred_edges)}")
        print(f"  Rejected Edges: {len(result.graph.rejected_edges)}")
        
        print(f"\nIdentified Root Causes:")
        for root in result.graph.get_roots():
            print(f"  * {root.name}")
            reasoning = result.graph.root_reasoning.get(root, "N/A")
            print(f"    > {reasoning[:120]}...")
        
        print(f"\nDiscovered Causal Relationships:")
        print(f"{'Source':<20} {'Target':<20} {'Confidence':<12} {'Mechanism'}")
        print("-" * 90)
        for edge in sorted(result.graph.edges, key=lambda e: e.confidence, reverse=True):
            mech_preview = edge.mechanism[:40] + "..." if len(edge.mechanism) > 40 else edge.mechanism
            print(f"{edge.source.name:<20} -> {edge.target.name:<18} {edge.confidence:<12.2f} {mech_preview}")
        
        if result.graph.deferred_edges:
            print(f"\nDeferred Edges (uncertain):")
            for edge, reason in result.graph.deferred_edges[:5]:
                print(f"  * {edge.source.name} -> {edge.target.name}: {reason}")
        
        if result.graph.rejected_edges:
            print(f"\nRejected Edges (top 5):")
            for edge, reason in result.graph.rejected_edges[:5]:
                print(f"  * {edge.source.name} -> {edge.target.name}: {reason[:60]}...")
        
        print(f"\nValidation Results:")
        for test_name, test_result in result.validation.tests.items():
            status = "[OK]" if test_result.passed else "[FAIL]"
            print(f"  {status} {test_name}: score={test_result.score:.2f}, violations={len(test_result.violations)}")
        
        # Uncertainty analysis
        low_conf = [e for e in result.graph.edges if e.confidence < 0.6]
        if low_conf:
            print(f"\nUncertainty Analysis:")
            print(f"  Edges with confidence < 0.6: {len(low_conf)}")
            for edge in low_conf:
                print(f"    * {edge.source.name} -> {edge.target.name}: {edge.confidence:.2f}")
        
        # Generate natural language explanation
        print("\n" + "="*70)
        print("NATURAL LANGUAGE EXPLANATION")
        print("="*70)
        
        explanation = discovery.explain_graph(result.graph)
        # Sanitize Unicode characters for Windows console
        explanation_clean = explanation.replace('→', '->').replace('•', '*').replace('✓', '[OK]').replace('✗', '[X]')
        print(f"\n{explanation_clean}\n")
        
        # Save all results
        print("="*70)
        print("SAVING RESULTS")
        print("="*70)
        
        os.makedirs('outputs', exist_ok=True)
        
        # Save data
        data.to_csv('outputs/health_data.csv', index=False)
        print("[OK] Data saved to outputs/health_data.csv")
        
        # Save report
        result.report.save('outputs/health_example_report.json')
        print("[OK] Report saved to outputs/health_example_report.json")
        
        # Save visualization
        result.graph.visualize('outputs/health_example_graph.png', figsize=(14, 10))
        print("[OK] Graph visualization saved to outputs/health_example_graph.png")
        
        # Save graph structure
        import json
        with open('outputs/health_example_graph.json', 'w') as f:
            json.dump(result.graph.to_dict(), f, indent=2)
        print("[OK] Graph structure saved to outputs/health_example_graph.json")
        
        # Save explanation (with Unicode handling)
        with open('outputs/health_example_explanation.txt', 'w', encoding='utf-8') as f:
            f.write(explanation)
        print("[OK] Explanation saved to outputs/health_example_explanation.txt")
        
        print("\n" + "="*70)
        print("DISCOVERY COMPLETE")
        print("="*70)
        print("\nCheck the 'outputs' directory for all saved results.")
        
    except Exception as e:
        print(f"\n[FAIL] Discovery failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


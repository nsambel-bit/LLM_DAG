"""Main orchestrator for hybrid causal discovery."""

import pandas as pd
from typing import List, Optional

from src.models.data_structures import (
    Variable,
    DiscoveryConfig,
    DiscoveryResult,
    Report,
)
from src.core.llm_client import LLMClient
from src.core.causal_graph import CausalGraph
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.modules.statistical_analyzer import StatisticalAnalyzer
from src.modules.graph_builder import ConfidentGraphBuilder
from src.modules.conflict_resolver import ConflictResolver
from src.modules.graph_validator import GraphValidator


class HybridCausalDiscovery:
    """
    Main orchestrator for hybrid causal discovery.
    
    Combines LLM knowledge extraction with statistical analysis to discover
    causal relationships from variable descriptions and optional observational data.
    """
    
    def __init__(self, llm_client: LLMClient, config: Optional[DiscoveryConfig] = None):
        """
        Initialize hybrid causal discovery system.
        
        Args:
            llm_client: LLM client for knowledge extraction
            config: Discovery configuration
        """
        self.config = config or DiscoveryConfig()
        
        # Initialize modules
        self.knowledge = KnowledgeExtractor(
            llm_client,
            temperature=self.config.temperature,
            n_samples=self.config.n_samples
        )
        self.stats = None  # Initialize when data provided
        self.builder = ConfidentGraphBuilder(self.knowledge)
        self.resolver = None
        self.validator = None
    
    def discover(
        self,
        variables: List[Variable],
        data: Optional[pd.DataFrame] = None,
        config: Optional[DiscoveryConfig] = None
    ) -> DiscoveryResult:
        """
        Discover causal relationships from variables and optional data.
        
        Args:
            variables: List of variables with names and descriptions
            data: Optional observational data (variables as columns)
            config: Discovery configuration (overrides default)
            
        Returns:
            DiscoveryResult with graph, report, and validation
        """
        config = config or self.config
        
        print(f"\n{'='*60}")
        print(f"Hybrid Causal Discovery")
        print(f"{'='*60}")
        print(f"Variables: {len(variables)}")
        print(f"Data: {f'{len(data)} samples' if data is not None else 'None'}")
        print(f"{'='*60}\n")
        
        # Initialize statistical analyzer if data provided
        if data is not None:
            print("Initializing statistical analyzer...")
            self.stats = StatisticalAnalyzer(data, config.significance_level)
            self.builder.stats = self.stats
            self.resolver = ConflictResolver(self.knowledge, self.stats)
            self.validator = GraphValidator(self.knowledge, self.stats)
        else:
            print("No data provided, using LLM knowledge only...")
            self.validator = GraphValidator(self.knowledge)
        
        # Phase 1: Initial graph construction
        print("\n" + "="*60)
        print("Phase 1: Building initial causal graph")
        print("="*60)
        graph = self.builder.discover(variables)
        print(f"\nInitial graph: {len(graph.edges)} edges, "
              f"{len(graph.get_roots())} roots")
        
        # Phase 2: Conflict resolution
        if config.resolve_conflicts and self.resolver:
            print("\n" + "="*60)
            print("Phase 2: Resolving conflicts")
            print("="*60)
            deferred = graph.get_deferred_edges()
            if deferred:
                print(f"Resolving {len(deferred)} deferred edges...")
                resolutions = self.resolver.resolve_conflicts(graph, deferred)
                graph.apply_resolutions(resolutions)
                print(f"Resolved: {len([r for r in resolutions if r.decision == 'ADD'])} added, "
                      f"{len([r for r in resolutions if r.decision == 'REJECT'])} rejected")
            else:
                print("No conflicts to resolve")
        
        # Phase 3: Validation
        print("\n" + "="*60)
        print("Phase 3: Validating graph")
        print("="*60)
        validation_report = self.validator.validate(graph)
        print(f"Validation: {'[OK] PASSED' if validation_report.is_satisfactory() else '[WARN] ISSUES FOUND'}")
        for test_name, result in validation_report.tests.items():
            status = "[OK]" if result.passed else "[FAIL]"
            print(f"  {status} {test_name}: score={result.score:.2f}")
        
        # Phase 4: Refinement
        if config.iterative_refinement and not validation_report.is_satisfactory():
            print("\n" + "="*60)
            print("Phase 4: Iterative refinement")
            print("="*60)
            graph = self.validator.iterative_refinement(
                graph,
                max_iterations=config.max_refinement_iterations
            )
            validation_report = self.validator.validate(graph)
            print(f"Final validation: {'[OK] PASSED' if validation_report.is_satisfactory() else '[WARN] ISSUES REMAIN'}")
        
        # Generate final report
        print("\n" + "="*60)
        print("Generating report")
        print("="*60)
        report = self._generate_report(graph, validation_report, variables, data)
        
        print(f"\n{'='*60}")
        print(f"Discovery Complete")
        print(f"{'='*60}")
        print(f"Final graph: {len(graph.edges)} edges")
        print(f"Average confidence: {graph.get_average_confidence():.2f}")
        print(f"{'='*60}\n")
        
        return DiscoveryResult(
            graph=graph,
            report=report,
            validation=validation_report
        )
    
    def explain_graph(self, graph: CausalGraph) -> str:
        """
        Generate natural language explanation of discovered graph.
        
        Args:
            graph: Discovered causal graph
            
        Returns:
            Natural language explanation
        """
        prompt = f"""Generate a comprehensive explanation of this causal graph:

Variables: {[v.name for v in graph.get_all_variables()]}

Edges:
{graph.format_edges_with_confidence()}

Provide:
1. Overall structure summary
2. Key causal pathways
3. Root causes and ultimate effects
4. Any interesting patterns or insights
5. Caveats and uncertainties

Write in clear, accessible language suitable for a general audience.
"""
        
        return self.knowledge.llm.complete(prompt, temperature=0.3)
    
    def _generate_report(
        self,
        graph: CausalGraph,
        validation: any,
        variables: List[Variable],
        data: Optional[pd.DataFrame]
    ) -> Report:
        """Generate comprehensive discovery report."""
        report = Report()
        
        # Summary statistics
        report.add_section('summary', {
            'n_variables': len(variables),
            'n_edges': len(graph.edges),
            'n_roots': len(graph.get_roots()),
            'avg_confidence': graph.get_average_confidence(),
            'has_data': data is not None,
            'n_samples': len(data) if data is not None else 0
        })
        
        # Variable list
        report.add_section('variables', [
            {'name': v.name, 'description': v.description}
            for v in variables
        ])
        
        # Root causes
        report.add_section('roots', [
            {
                'name': root.name,
                'reasoning': graph.root_reasoning.get(root, 'N/A')
            }
            for root in graph.get_roots()
        ])
        
        # Edge details
        report.add_section('edges', [
            {
                'source': e.source.name,
                'target': e.target.name,
                'confidence': e.confidence,
                'mechanism': e.mechanism,
            }
            for e in sorted(graph.edges, key=lambda x: x.confidence, reverse=True)
        ])
        
        # Validation results
        report.add_section('validation', validation.to_dict())
        
        # Uncertainty analysis
        low_confidence_edges = [e for e in graph.edges if e.confidence < 0.5]
        report.add_section('uncertainty', {
            'n_low_confidence': len(low_confidence_edges),
            'edges': [
                {
                    'source': e.source.name,
                    'target': e.target.name,
                    'confidence': e.confidence,
                }
                for e in low_confidence_edges
            ]
        })
        
        # Rejected edges (for transparency)
        report.add_section('rejected', [
            {
                'source': edge.source.name,
                'target': edge.target.name,
                'reason': reason
            }
            for edge, reason in graph.rejected_edges[:10]  # Top 10
        ])
        
        return report


"""Validation and refinement of discovered causal graphs."""

import re
from typing import List, Optional

from src.models.data_structures import (
    Variable,
    ValidationReport,
    TestResult,
    Violation,
    Refinement,
)
from src.core.causal_graph import CausalGraph
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.modules.statistical_analyzer import StatisticalAnalyzer


class GraphValidator:
    """
    Validate and refine discovered causal graphs.
    """
    
    def __init__(
        self,
        knowledge_extractor: KnowledgeExtractor,
        statistical_analyzer: Optional[StatisticalAnalyzer] = None
    ):
        """
        Initialize graph validator.
        
        Args:
            knowledge_extractor: Knowledge extraction module
            statistical_analyzer: Optional statistical analysis module
        """
        self.knowledge = knowledge_extractor
        self.stats = statistical_analyzer
    
    def validate(self, graph: CausalGraph) -> ValidationReport:
        """
        Comprehensive validation of discovered graph.
        
        Args:
            graph: Causal graph to validate
            
        Returns:
            Validation report with test results
        """
        report = ValidationReport(graph=graph)
        
        # Test 1: Structural validity
        report.add_test('structural', self._test_structure(graph))
        
        # Test 2: Edge confidence distribution
        report.add_test('confidence', self._test_confidence_distribution(graph))
        
        # Test 3: Statistical consistency (if data available)
        if self.stats:
            report.add_test('statistical', self._test_statistical_consistency(graph))
        
        # Test 4: Logical consistency
        report.add_test('logical', self._test_logical_consistency(graph))
        
        # Test 5: Completeness check
        report.add_test('completeness', self._test_completeness(graph))
        
        return report
    
    def iterative_refinement(
        self,
        graph: CausalGraph,
        max_iterations: int = 3
    ) -> CausalGraph:
        """
        Iteratively refine graph based on validation feedback.
        
        Args:
            graph: Current causal graph
            max_iterations: Maximum refinement iterations
            
        Returns:
            Refined causal graph
        """
        for iteration in range(max_iterations):
            print(f"  Refinement iteration {iteration + 1}/{max_iterations}...")
            
            # Validate current graph
            report = self.validate(graph)
            
            if report.is_satisfactory():
                print("  Graph validation satisfactory")
                break
            
            # Identify issues
            issues = report.get_issues()
            print(f"    Found {len(issues)} issues")
            
            # Propose refinements
            refinements = self._propose_refinements(graph, issues)
            
            if not refinements:
                print("  No refinements proposed")
                break
            
            # Apply refinements
            for refinement in refinements[:5]:  # Limit to 5 per iteration
                try:
                    if refinement.type == 'MODIFY_CONFIDENCE':
                        # Update confidence for existing edge
                        for edge in graph.edges:
                            if (edge.source.name == refinement.params['source'] and
                                edge.target.name == refinement.params['target']):
                                edge.confidence = refinement.params['confidence']
                except Exception as e:
                    print(f"    Failed to apply refinement: {e}")
        
        return graph
    
    def _test_structure(self, graph: CausalGraph) -> TestResult:
        """Test structural validity of graph."""
        violations = []
        
        # Check 1: No cycles (already enforced during construction)
        # Check 2: At least one root
        if len(graph.get_roots()) == 0:
            violations.append(Violation(
                type='no_roots',
                details='Graph has no root causes',
                severity='high'
            ))
        
        # Check 3: No isolated nodes
        all_vars = graph.get_all_variables()
        for var in all_vars:
            if len(graph.get_edges_from(var)) == 0 and len(graph.get_edges_to(var)) == 0:
                violations.append(Violation(
                    type='isolated_node',
                    details=f'Variable {var.name} is isolated',
                    severity='medium'
                ))
        
        return TestResult(
            passed=len(violations) == 0,
            violations=violations,
            score=1.0 - (len(violations) * 0.2)
        )
    
    def _test_confidence_distribution(self, graph: CausalGraph) -> TestResult:
        """Test distribution of confidence scores."""
        violations = []
        
        if not graph.edges:
            return TestResult(passed=True, violations=[], score=1.0)
        
        confidences = [e.confidence for e in graph.edges]
        avg_conf = sum(confidences) / len(confidences)
        
        # Check 1: Average confidence too low
        if avg_conf < 0.5:
            violations.append(Violation(
                type='low_confidence',
                details=f'Average confidence is low: {avg_conf:.2f}',
                severity='medium'
            ))
        
        # Check 2: Too many low-confidence edges
        low_conf_edges = [e for e in graph.edges if e.confidence < 0.4]
        if len(low_conf_edges) > len(graph.edges) * 0.3:
            violations.append(Violation(
                type='many_low_confidence',
                details=f'{len(low_conf_edges)} edges with confidence < 0.4',
                severity='medium'
            ))
        
        return TestResult(
            passed=len(violations) == 0,
            violations=violations,
            score=min(1.0, avg_conf)
        )
    
    def _test_statistical_consistency(self, graph: CausalGraph) -> TestResult:
        """Test if graph is consistent with conditional independencies."""
        violations = []
        
        # Sample a subset of edges for testing
        test_edges = graph.edges[:min(10, len(graph.edges))]
        
        for edge in test_edges:
            try:
                # Get conditioning set
                parents = graph.get_parents(edge.target)
                other_parents = [p for p in parents if p != edge.source]
                
                if other_parents:
                    # Test if source and target are independent given other parents
                    evidence = self.stats.compute_evidence_profile(
                        edge.source,
                        edge.target,
                        conditioning_set=other_parents
                    )
                    
                    if evidence.cond_independence_test:
                        if (evidence.cond_independence_test.independent and
                            evidence.cond_independence_test.p_value < 0.01):
                            violations.append(Violation(
                                type='conditional_independence',
                                edge=edge,
                                details=f'{edge.source.name} independent of {edge.target.name} given parents',
                                p_value=evidence.cond_independence_test.p_value,
                                severity='high'
                            ))
            except Exception as e:
                # Skip if test fails
                continue
        
        return TestResult(
            passed=len(violations) == 0,
            violations=violations,
            score=1.0 - (len(violations) / max(len(test_edges), 1))
        )
    
    def _test_logical_consistency(self, graph: CausalGraph) -> TestResult:
        """Test logical consistency using LLM."""
        violations = []
        
        # Sample paths to verify
        all_paths = graph.get_all_paths(max_length=3)
        test_paths = all_paths[:min(5, len(all_paths))]
        
        for path in test_paths:
            if len(path) < 2:
                continue
            
            # Ask LLM if this causal chain makes sense
            prompt = f"""            The discovered causal graph implies this causal chain:
            {' -> '.join([v.name for v in path])}

Descriptions:
{self._format_path_descriptions(path)}

Does this causal chain make logical sense?
- Consider: temporal ordering, mechanism plausibility, domain knowledge
- Rate plausibility: 0-1
- If implausible (< 0.5), explain why

<plausibility>0.XX</plausibility>
<reasoning>...</reasoning>
"""
            
            try:
                response = self.knowledge.llm.complete(prompt, temperature=0.1)
                parsed = self._parse_plausibility(response)
                
                if parsed['plausibility'] < 0.5:
                    violations.append(Violation(
                        type='implausible_path',
                        details=f"Path: {' -> '.join([v.name for v in path])}. Reason: {parsed['reasoning']}",
                        severity='medium'
                    ))
            except:
                # Skip if LLM call fails
                continue
        
        return TestResult(
            passed=len(violations) == 0,
            violations=violations,
            score=1.0 - (len(violations) / max(len(test_paths), 1))
        )
    
    def _test_completeness(self, graph: CausalGraph) -> TestResult:
        """Test if graph is complete."""
        violations = []
        
        # Check 1: Are there enough edges?
        n_vars = len(graph.get_all_variables())
        n_edges = len(graph.edges)
        
        # Heuristic: expect at least n_vars - 1 edges (minimum spanning)
        if n_edges < max(1, n_vars - 1):
            violations.append(Violation(
                type='too_sparse',
                details=f'Only {n_edges} edges for {n_vars} variables',
                severity='low'
            ))
        
        # Check 2: Are there variables with no connections?
        for var in graph.get_all_variables():
            in_degree = len(graph.get_edges_to(var))
            out_degree = len(graph.get_edges_from(var))
            
            if in_degree == 0 and out_degree == 0 and var not in graph.roots:
                violations.append(Violation(
                    type='disconnected',
                    details=f'Variable {var.name} has no connections',
                    severity='medium'
                ))
        
        return TestResult(
            passed=len(violations) == 0,
            violations=violations,
            score=1.0 - (len(violations) * 0.1)
        )
    
    def _propose_refinements(
        self,
        graph: CausalGraph,
        issues: List[Violation]
    ) -> List[Refinement]:
        """Propose refinements based on validation issues."""
        refinements = []
        
        for issue in issues:
            if issue.type == 'low_confidence' and issue.edge:
                # Consider removing very low confidence edges
                if issue.edge.confidence < 0.3:
                    refinements.append(Refinement(
                        type='REMOVE_EDGE',
                        params={
                            'source': issue.edge.source.name,
                            'target': issue.edge.target.name
                        }
                    ))
            
            elif issue.type == 'conditional_independence' and issue.edge:
                # Reduce confidence for conditionally independent edges
                refinements.append(Refinement(
                    type='MODIFY_CONFIDENCE',
                    params={
                        'source': issue.edge.source.name,
                        'target': issue.edge.target.name,
                        'confidence': max(0.2, issue.edge.confidence * 0.5)
                    }
                ))
        
        return refinements
    
    def _format_path_descriptions(self, path: List[Variable]) -> str:
        """Format variable descriptions for a path."""
        return "\n".join([
            f"- {v.name}: {v.description}"
            for v in path
        ])
    
    def _parse_plausibility(self, response: str) -> dict:
        """Parse plausibility assessment from LLM response."""
        parsed = {}
        
        # Extract plausibility score
        plaus_match = re.search(r'<plausibility>([\d\.]+)</plausibility>', response)
        if plaus_match:
            try:
                parsed['plausibility'] = float(plaus_match.group(1))
            except:
                parsed['plausibility'] = 0.5
        else:
            parsed['plausibility'] = 0.5
        
        # Extract reasoning
        reason_match = re.search(r'<reasoning>(.*?)</reasoning>', response, re.DOTALL)
        if reason_match:
            parsed['reasoning'] = reason_match.group(1).strip()
        else:
            parsed['reasoning'] = "No reasoning provided"
        
        return parsed


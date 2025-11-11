"""Graph construction using BFS with confidence tracking."""

from queue import PriorityQueue
from typing import List, Optional, Set, Tuple
from datetime import datetime
import numpy as np

from src.models.data_structures import (
    Variable,
    CausalEdge,
    GraphContext,
    EdgeDecision,
    Refinement,
)
from src.core.causal_graph import CausalGraph
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.modules.statistical_analyzer import StatisticalAnalyzer


class ConfidentGraphBuilder:
    """
    Construct causal graph using BFS with confidence tracking and uncertainty quantification.
    """
    
    def __init__(
        self,
        knowledge_extractor: KnowledgeExtractor,
        statistical_analyzer: Optional[StatisticalAnalyzer] = None
    ):
        """
        Initialize graph builder.
        
        Args:
            knowledge_extractor: Knowledge extraction module
            statistical_analyzer: Optional statistical analysis module
        """
        self.knowledge = knowledge_extractor
        self.stats = statistical_analyzer
        self.graph = CausalGraph()
    
    def discover(self, variables: List[Variable]) -> CausalGraph:
        """
        Main discovery algorithm using BFS with confidence tracking.
        
        Args:
            variables: List of all variables to consider
            
        Returns:
            Discovered causal graph
        """
        # Stage 1: Initialize with root causes
        print("  Identifying root causes...")
        roots = self.knowledge.identify_root_causes(variables)
        queue = PriorityQueue()
        counter = 0  # Counter for tie-breaking in priority queue
        
        for root in roots:
            if root.confidence > 0.5:
                # Use counter as tiebreaker to avoid comparing Variable objects
                queue.put((-root.confidence, counter, root.variable))
                counter += 1
                self.graph.mark_as_root(root.variable, root.reasoning)
            else:
                self.graph.add_uncertain_root(root.variable, root.confidence)
        
        if queue.empty():
            print("  Warning: No confident root causes found, using all variables")
            for i, var in enumerate(variables[:2]):  # Start with first 2 variables
                queue.put((0.0, counter + i, var))
                self.graph.mark_as_root(var, "Fallback: no confident roots")
            counter += 2
        
        visited = set()
        deferred_nodes = []
        
        # Stage 2: BFS Expansion
        print(f"  Expanding graph from {queue.qsize()} root(s)...")
        iteration = 0
        
        while not queue.empty() and iteration < 100:  # Safety limit
            neg_confidence, _, node = queue.get()  # Extract from (priority, counter, node) tuple
            iteration += 1
            
            if node in visited:
                continue
            
            visited.add(node)
            self.graph.mark_visited(node)
            
            print(f"    Expanding {node.name}...")
            
            # Build context
            context = self._build_context(node, visited, variables)
            
            # Expand node to find effects
            edges = self.knowledge.expand_node(node, self.graph, context)
            
            if not edges:
                continue
            
            # Process each proposed edge
            for edge in edges:
                decision = self._evaluate_edge(edge)
                
                if decision.action == 'ADD':
                    self._add_edge(edge)
                    if edge.target not in visited:
                        queue.put((-edge.confidence, counter, edge.target))
                        counter += 1
                
                elif decision.action == 'DEFER':
                    deferred_nodes.append((edge, decision.reason))
                    self.graph.add_deferred_edge(edge, decision.reason)
                
                elif decision.action == 'REJECT':
                    self.graph.add_rejected_edge(edge, decision.reason)
        
        print(f"  Graph construction complete: {len(self.graph.edges)} edges")
        
        # Stage 3: Process deferred nodes with more context
        if deferred_nodes:
            print(f"  Processing {len(deferred_nodes)} deferred edges...")
            # Note: Detailed resolution happens in ConflictResolver
        
        return self.graph
    
    def _build_context(
        self,
        node: Variable,
        visited: Set[Variable],
        all_variables: List[Variable]
    ) -> GraphContext:
        """Build context for node expansion."""
        context = GraphContext(all_variables=all_variables)
        context.visited = visited.copy()
        return context
    
    def _evaluate_edge(self, edge: CausalEdge) -> EdgeDecision:
        """
        Decide whether to add, defer, or reject an edge.
        
        Args:
            edge: Proposed causal edge
            
        Returns:
            Decision with reasoning
        """
        decision = EdgeDecision(edge=edge)
        
        # Check 1: Cycle detection
        if self._creates_cycle(edge):
            decision.action = 'REJECT'
            decision.reason = 'Would create cycle'
            decision.confidence = 1.0
            return decision
        
        # Check 2: LLM confidence
        if edge.confidence < 0.3:
            decision.action = 'DEFER'
            decision.reason = 'Low LLM confidence'
            return decision
        
        # Check 3: Statistical compatibility (if data available)
        if self.stats:
            try:
                evidence = self.stats.compute_evidence_profile(
                    edge.source,
                    edge.target
                )
                compatibility = self.stats.test_edge_compatibility(edge, evidence)
                
                if not compatibility.compatible:
                    if self._has_strong_conflict(compatibility):
                        decision.action = 'DEFER'
                        decision.reason = 'Statistical conflict'
                        decision.evidence = evidence
                        return decision
            except Exception as e:
                # If statistical analysis fails, rely on LLM
                pass
        
        # Check 4: Combined confidence
        combined_confidence = self._compute_combined_confidence(edge)
        
        if combined_confidence > 0.6:
            decision.action = 'ADD'
            decision.confidence = combined_confidence
        else:
            decision.action = 'DEFER'
            decision.reason = 'Uncertain combined confidence'
            decision.confidence = combined_confidence
        
        return decision
    
    def _creates_cycle(self, edge: CausalEdge) -> bool:
        """Check if adding edge would create a cycle."""
        return self.graph.would_create_cycle(edge.source, edge.target)
    
    def _has_strong_conflict(self, compatibility) -> bool:
        """Check if there are strong conflicts in compatibility assessment."""
        strong_conflicts = [
            s for s in compatibility.signals
            if s.severity == 'strong_conflict'
        ]
        return len(strong_conflicts) > 0
    
    def _compute_combined_confidence(self, edge: CausalEdge) -> float:
        """
        Combine LLM confidence with statistical evidence.
        
        Args:
            edge: Causal edge
            
        Returns:
            Combined confidence score
        """
        llm_conf = edge.confidence
        
        if not self.stats:
            return llm_conf
        
        try:
            # Get statistical evidence
            evidence = self.stats.compute_evidence_profile(
                edge.source,
                edge.target
            )
            
            # Statistical confidence based on multiple signals
            stat_signals = []
            
            # Signal 1: Correlation strength
            if abs(evidence.correlation) > 0.5:
                stat_signals.append(0.7)
            elif abs(evidence.correlation) > 0.3:
                stat_signals.append(0.5)
            else:
                stat_signals.append(0.2)
            
            # Signal 2: Granger causality
            if evidence.granger_causality:
                if evidence.granger_causality.forward_significant:
                    stat_signals.append(0.8)
                elif evidence.granger_causality.reverse_direction:
                    stat_signals.append(0.1)
                else:
                    stat_signals.append(0.4)
            
            # Signal 3: Effect size
            if evidence.intervention_effect:
                if abs(evidence.intervention_effect.coefficient) > 0.5:
                    stat_signals.append(0.7)
                else:
                    stat_signals.append(0.4)
            
            stat_conf = np.mean(stat_signals) if stat_signals else 0.5
            
            # Weighted combination (favor LLM for domain knowledge)
            alpha = 0.6  # Weight for LLM
            combined = alpha * llm_conf + (1 - alpha) * stat_conf
            
            return combined
        
        except Exception:
            # If statistical analysis fails, use LLM confidence
            return llm_conf
    
    def _add_edge(self, edge: CausalEdge):
        """Add edge to graph with full metadata."""
        self.graph.add_edge(
            source=edge.source,
            target=edge.target,
            confidence=edge.confidence,
            mechanism=edge.mechanism,
            evidence=edge.evidence if hasattr(edge, 'evidence') else None,
            timestamp=datetime.now()
        )


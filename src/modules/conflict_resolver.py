"""Conflict resolution between knowledge-based and data-driven signals."""

import re
from typing import List, Tuple

from src.models.data_structures import (
    CausalEdge,
    Resolution,
)
from src.core.causal_graph import CausalGraph
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.modules.statistical_analyzer import StatisticalAnalyzer


class ConflictResolver:
    """
    Resolve conflicts between knowledge-based and data-driven signals.
    """
    
    def __init__(
        self,
        knowledge_extractor: KnowledgeExtractor,
        statistical_analyzer: StatisticalAnalyzer
    ):
        """
        Initialize conflict resolver.
        
        Args:
            knowledge_extractor: Knowledge extraction module
            statistical_analyzer: Statistical analysis module
        """
        self.knowledge = knowledge_extractor
        self.stats = statistical_analyzer
    
    def resolve_conflicts(
        self,
        graph: CausalGraph,
        deferred_edges: List[Tuple[CausalEdge, str]]
    ) -> List[Resolution]:
        """
        Resolve all deferred/conflicted edges.
        
        Args:
            graph: Current causal graph
            deferred_edges: List of (edge, reason) tuples
            
        Returns:
            List of resolutions
        """
        resolutions = []
        
        for edge, reason in deferred_edges:
            print(f"    Resolving: {edge.source.name} -> {edge.target.name}")
            resolution = self._resolve_single_conflict(edge, reason, graph)
            resolutions.append(resolution)
            
            if resolution.decision == 'ADD':
                graph.add_edge(
                    edge.source,
                    edge.target,
                    confidence=resolution.revised_confidence,
                    mechanism=edge.mechanism,
                    notes=resolution.explanation
                )
            elif resolution.decision == 'REJECT':
                graph.add_rejected_edge(edge, resolution.explanation)
        
        return resolutions
    
    def _resolve_single_conflict(
        self,
        edge: CausalEdge,
        reason: str,
        graph: CausalGraph
    ) -> Resolution:
        """
        Resolve a single edge conflict through LLM-data dialogue.
        
        Args:
            edge: Conflicted edge
            reason: Reason for conflict
            graph: Current graph
            
        Returns:
            Resolution decision
        """
        # Gather evidence
        try:
            evidence = self.stats.compute_evidence_profile(
                edge.source,
                edge.target
            )
            narrative = self.stats.generate_statistical_narrative(
                edge.source,
                edge.target,
                evidence
            )
        except Exception as e:
            evidence = None
            narrative = f"Statistical analysis unavailable: {str(e)}"
        
        # Present conflict to LLM
        prompt = self._build_conflict_resolution_prompt(
            edge=edge,
            original_confidence=edge.confidence,
            conflict_reason=reason,
            statistical_evidence=narrative,
            graph_context=graph
        )
        
        try:
            response = self.knowledge.llm.complete(prompt, temperature=0.1)
            parsed = self._parse_resolution(response)
            
            return Resolution(
                edge=edge,
                decision=parsed['decision'],
                revised_confidence=parsed['confidence'],
                explanation=parsed['explanation'],
                alternative_hypothesis=parsed.get('alternative'),
                original_evidence=evidence
            )
        except Exception as e:
            # Fallback: conservative decision
            return Resolution(
                edge=edge,
                decision='REJECT',
                revised_confidence=0.0,
                explanation=f"Resolution failed: {str(e)}",
                original_evidence=evidence
            )
    
    def _build_conflict_resolution_prompt(
        self,
        edge: CausalEdge,
        original_confidence: float,
        conflict_reason: str,
        statistical_evidence: str,
        graph_context: CausalGraph
    ) -> str:
        """Build prompt for LLM to reconsider edge."""
        return f"""You previously suggested a causal relationship with confidence {original_confidence:.2f}:
{edge.source.name} -> {edge.target.name}

Your reasoning: {edge.mechanism}

However, there is a conflict: {conflict_reason}

Statistical Evidence:
{statistical_evidence}

Current graph structure:
{graph_context.summarize()}

Please reconsider this relationship. Provide:

1. DECISION: Should this edge be:
   - ADDED (you're confident despite statistical noise)
   - REJECTED (statistical evidence convincingly refutes it)
   - MODIFIED (different relationship, e.g., reverse direction or mediated)

2. REVISED CONFIDENCE (0-1): Your updated confidence

3. EXPLANATION: Reconcile your domain knowledge with statistical evidence
   - If ADDED: Why statistical evidence is misleading or incomplete
   - If REJECTED: What you initially overlooked
   - If MODIFIED: What the actual relationship is

4. ALTERNATIVE HYPOTHESIS (if any):
   - Could there be a confounder?
   - Is the relationship indirect?
   - Is there reverse causation?

Response format:
<decision>ADD|REJECT|MODIFY</decision>
<confidence>0.XX</confidence>
<explanation>
[Your detailed reasoning]
</explanation>
<alternative>
[If applicable, alternative causal structure]
</alternative>
"""
    
    def _parse_resolution(self, response: str) -> dict:
        """Parse resolution from LLM response."""
        parsed = {}
        
        # Extract decision
        decision_match = re.search(r'<decision>(.*?)</decision>', response, re.IGNORECASE)
        if decision_match:
            decision = decision_match.group(1).strip().upper()
            # Map MODIFY to ADD for simplicity
            parsed['decision'] = 'ADD' if decision == 'MODIFY' else decision
        else:
            parsed['decision'] = 'REJECT'  # Conservative default
        
        # Extract confidence
        conf_match = re.search(r'<confidence>([\d\.]+)</confidence>', response)
        if conf_match:
            try:
                parsed['confidence'] = float(conf_match.group(1))
            except:
                parsed['confidence'] = 0.3
        else:
            parsed['confidence'] = 0.3
        
        # Extract explanation
        expl_match = re.search(r'<explanation>(.*?)</explanation>', response, re.DOTALL)
        if expl_match:
            parsed['explanation'] = expl_match.group(1).strip()
        else:
            parsed['explanation'] = "No explanation provided"
        
        # Extract alternative
        alt_match = re.search(r'<alternative>(.*?)</alternative>', response, re.DOTALL)
        if alt_match:
            parsed['alternative'] = alt_match.group(1).strip()
        else:
            parsed['alternative'] = None
        
        return parsed


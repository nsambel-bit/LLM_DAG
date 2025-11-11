"""Knowledge extraction from LLM with confidence scoring."""

import re
from typing import List, Optional
from collections import Counter

from src.models.data_structures import (
    Variable,
    CausalEdge,
    RootNode,
    Explanation,
    GraphContext,
)
from src.core.causal_graph import CausalGraph


class KnowledgeExtractor:
    """
    Extracts causal relationships using LLM with confidence scores.
    Uses self-consistency sampling for uncertainty quantification.
    """
    
    def __init__(self, llm_client, temperature: float = 0.3, n_samples: int = 5):
        """
        Initialize knowledge extractor.
        
        Args:
            llm_client: LLM client for API calls
            temperature: Sampling temperature
            n_samples: Number of samples for self-consistency
        """
        self.llm = llm_client
        self.temperature = temperature
        self.n_samples = n_samples
    
    def identify_root_causes(self, variables: List[Variable]) -> List[RootNode]:
        """
        Identify variables that are root causes (not caused by others).
        
        Args:
            variables: List of all variables
            
        Returns:
            List of root nodes with confidence scores
        """
        prompt = self._build_root_prompt(variables)
        
        # Sample multiple times for self-consistency
        samples = []
        for _ in range(self.n_samples):
            response = self.llm.complete(prompt=prompt, temperature=self.temperature)
            samples.append(self._parse_roots(response))
        
        # Aggregate results with confidence
        root_candidates = self._aggregate_samples(samples)
        
        # Map string names back to Variable objects
        name_to_var = {v.name: v for v in variables}
        
        result = []
        for var_name in root_candidates:
            # Find matching variable
            matched_var = None
            for var in variables:
                if var.name.lower() == var_name.lower():
                    matched_var = var
                    break
            
            if matched_var:
                result.append(RootNode(
                    variable=matched_var,
                    confidence=self._compute_confidence(var_name, samples),
                    reasoning=self._extract_reasoning(var_name, samples, variables)
                ))
        
        return result
    
    def expand_node(
        self,
        node: Variable,
        current_graph: CausalGraph,
        context: GraphContext
    ) -> List[CausalEdge]:
        """
        Find all variables directly caused by the current node.
        
        Args:
            node: Current node to expand
            current_graph: Current state of the graph
            context: Graph construction context
            
        Returns:
            List of causal edges with confidence scores
        """
        prompt = self._build_expansion_prompt(node, current_graph, context)
        
        # Multi-sample for confidence
        edge_samples = []
        for _ in range(self.n_samples):
            response = self.llm.complete(prompt, self.temperature)
            edge_samples.append(self._parse_edges(response, context.all_variables))
        
        # Return edges with confidence and mechanisms
        edges = []
        aggregated = self._aggregate_edge_samples(edge_samples)
        
        for target, mechanism in aggregated.items():
            edges.append(CausalEdge(
                source=node,
                target=target,
                confidence=self._compute_edge_confidence(node, target, edge_samples),
                mechanism=mechanism,
                alternative_explanations=self._extract_alternatives(
                    node, target, edge_samples
                )
            ))
        
        return edges
    
    def explain_relationship(self, edge: CausalEdge, evidence: dict) -> Explanation:
        """
        Generate detailed explanation for a causal relationship.
        
        Args:
            edge: Causal edge to explain
            evidence: Additional evidence
            
        Returns:
            Detailed explanation
        """
        prompt = f"""
Explain the causal relationship: {edge.source.name} -> {edge.target.name}

Variable Descriptions:
{edge.source.name}: {edge.source.description}
{edge.target.name}: {edge.target.description}

Provide:
1. Causal mechanism (how does source affect target?)
2. Time scale (immediate, short-term, long-term?)
3. Nature (linear, threshold, complex?)
4. Potential confounders
5. Boundary conditions (when does this hold?)
6. Confidence level (1-5) with justification

Format your response as:
<mechanism>...</mechanism>
<time_scale>...</time_scale>
<nature>...</nature>
<confounders>...</confounders>
<boundary_conditions>...</boundary_conditions>
<confidence>...</confidence>
<justification>...</justification>
"""
        
        response = self.llm.complete(prompt, temperature=0.1)
        return self._parse_explanation(response)
    
    def _build_root_prompt(self, variables: List[Variable]) -> str:
        """Build prompt for root cause identification."""
        var_descriptions = "\n".join([
            f"- {v.name}: {v.description}"
            for v in variables
        ])
        
        return f"""You are a causal reasoning expert. Analyze these variables and identify which ones are ROOT CAUSES (not caused by any other variables in this set).

Variables:
{var_descriptions}

Think step-by-step:
1. For each variable, consider what could cause it
2. Check if potential causes are in the variable set
3. Only select variables with no causes in the set

Response format:
<reasoning>
[Your step-by-step analysis]
</reasoning>

<root_causes>
[Variable names only, one per line]
</root_causes>
"""
    
    def _build_expansion_prompt(
        self,
        node: Variable,
        graph_state: CausalGraph,
        context: GraphContext
    ) -> str:
        """Build prompt for node expansion."""
        existing_edges = graph_state.get_edges_summary()
        remaining_vars = [
            v for v in context.all_variables
            if not graph_state.is_visited(v) and v != node
        ]
        
        remaining_desc = "\n".join([
            f"- {v.name}: {v.description}"
            for v in remaining_vars
        ])
        
        return f"""Current causal graph construction state:

Current Node: {node.name}
Description: {node.description}

Already discovered relationships:
{existing_edges if existing_edges != "No edges yet" else "None yet"}

Remaining variables to consider:
{remaining_desc if remaining_desc else "None"}

Task: Determine which remaining variables are DIRECTLY caused by {node.name}.

Consider:
1. Direct vs indirect effects (only include direct)
2. Temporal ordering (cause must precede effect)
3. Mechanism plausibility
4. Alternative explanations (common cause, reverse causation)

For each potential effect, provide:
- Variable name
- Confidence (0-1)
- Causal mechanism (brief)

Response format:
<analysis>
[Your reasoning for each variable]
</analysis>

<direct_effects>
Variable: [name]
Confidence: [0-1]
Mechanism: [brief explanation]
---
[Repeat for each direct effect]
</direct_effects>
"""
    
    def _parse_roots(self, response: str) -> List[str]:
        """Parse root causes from LLM response."""
        match = re.search(r'<root_causes>(.*?)</root_causes>', response, re.DOTALL)
        if not match:
            return []
        
        content = match.group(1).strip()
        roots = [
            line.strip()
            for line in content.split('\n')
            if line.strip() and not line.strip().startswith('-')
        ]
        
        # Clean up root names
        cleaned_roots = []
        for root in roots:
            # Remove leading dashes, numbers, etc.
            cleaned = re.sub(r'^[-\d\.\)]+\s*', '', root).strip()
            if cleaned:
                cleaned_roots.append(cleaned)
        
        return cleaned_roots
    
    def _parse_edges(
        self,
        response: str,
        all_variables: List[Variable]
    ) -> List[tuple]:
        """Parse edges from expansion response."""
        edges = []
        
        match = re.search(r'<direct_effects>(.*?)</direct_effects>', response, re.DOTALL)
        if not match:
            return edges
        
        content = match.group(1).strip()
        
        # Split by separator
        blocks = content.split('---')
        
        for block in blocks:
            if not block.strip():
                continue
            
            # Extract variable name
            var_match = re.search(r'Variable:\s*(.+)', block)
            # Extract confidence
            conf_match = re.search(r'Confidence:\s*([\d\.]+)', block)
            # Extract mechanism
            mech_match = re.search(r'Mechanism:\s*(.+?)(?=\n|$)', block, re.DOTALL)
            
            if var_match and conf_match and mech_match:
                var_name = var_match.group(1).strip()
                confidence = float(conf_match.group(1))
                mechanism = mech_match.group(1).strip()
                
                # Find matching variable
                target_var = None
                for var in all_variables:
                    if var.name.lower() == var_name.lower():
                        target_var = var
                        break
                
                if target_var:
                    edges.append((target_var, confidence, mechanism))
        
        return edges
    
    def _aggregate_samples(self, samples: List[List[str]]) -> List[Variable]:
        """Aggregate root cause samples."""
        # This is a placeholder - in practice, need to match variable names
        all_roots = []
        for sample in samples:
            all_roots.extend(sample)
        
        # Count occurrences
        root_counts = Counter(all_roots)
        
        # Return roots that appear in majority of samples
        threshold = self.n_samples / 2
        return [root for root, count in root_counts.items() if count >= threshold]
    
    def _aggregate_edge_samples(
        self,
        edge_samples: List[List[tuple]]
    ) -> dict:
        """Aggregate edge samples into consensus edges."""
        # Count how often each target appears
        target_counts = Counter()
        target_mechanisms = {}
        
        for sample in edge_samples:
            for target, conf, mechanism in sample:
                target_counts[target] += 1
                if target not in target_mechanisms:
                    target_mechanisms[target] = []
                target_mechanisms[target].append(mechanism)
        
        # Return targets that appear in at least half of samples
        threshold = self.n_samples / 2
        result = {}
        for target, count in target_counts.items():
            if count >= threshold:
                # Use most common mechanism
                result[target] = target_mechanisms[target][0]
        
        return result
    
    def _compute_confidence(self, var_name: str, samples: List[List[str]]) -> float:
        """Compute confidence for a root variable."""
        count = sum(1 for sample in samples if var_name in sample)
        return count / len(samples)
    
    def _compute_edge_confidence(
        self,
        source: Variable,
        target: Variable,
        edge_samples: List[List[tuple]]
    ) -> float:
        """Compute confidence for an edge."""
        appearances = 0
        total_conf = 0.0
        
        for sample in edge_samples:
            for t, conf, _ in sample:
                if t == target:
                    appearances += 1
                    total_conf += conf
                    break
        
        if appearances == 0:
            return 0.0
        
        # Combine frequency and average confidence
        frequency = appearances / len(edge_samples)
        avg_conf = total_conf / appearances
        
        return (frequency + avg_conf) / 2
    
    def _extract_reasoning(
        self,
        var_name: str,
        samples: List[List[str]],
        variables: List[Variable]
    ) -> str:
        """Extract reasoning for why variable is a root."""
        return f"{var_name} appears as root cause in {sum(1 for s in samples if var_name in s)}/{len(samples)} samples"
    
    def _extract_alternatives(
        self,
        source: Variable,
        target: Variable,
        samples: List[List[tuple]]
    ) -> List[str]:
        """Extract alternative explanations from samples."""
        alternatives = []
        
        # Collect all mechanisms mentioned
        mechanisms = []
        for sample in samples:
            for t, _, mechanism in sample:
                if t == target:
                    mechanisms.append(mechanism)
        
        # Return unique mechanisms (simplified)
        return list(set(mechanisms))[:3]  # Top 3 alternatives
    
    def _parse_explanation(self, response: str) -> Explanation:
        """Parse detailed explanation from LLM response."""
        def extract_tag(tag: str) -> str:
            match = re.search(f'<{tag}>(.*?)</{tag}>', response, re.DOTALL)
            return match.group(1).strip() if match else "Not specified"
        
        # Extract confidence level (1-5)
        conf_str = extract_tag('confidence')
        try:
            conf_level = int(re.search(r'\d+', conf_str).group())
        except:
            conf_level = 3
        
        # Extract confounders list
        confounders_str = extract_tag('confounders')
        confounders = [
            c.strip() for c in confounders_str.split(',')
            if c.strip()
        ]
        
        return Explanation(
            mechanism=extract_tag('mechanism'),
            time_scale=extract_tag('time_scale'),
            nature=extract_tag('nature'),
            potential_confounders=confounders,
            boundary_conditions=extract_tag('boundary_conditions'),
            confidence_level=conf_level,
            justification=extract_tag('justification')
        )


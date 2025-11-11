"""Causal graph data structure and operations."""

from typing import List, Set, Optional, Dict, Tuple, Any
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

from src.models.data_structures import Variable, CausalEdge


class CausalGraph:
    """Represents a causal directed acyclic graph (DAG)."""
    
    def __init__(self):
        """Initialize empty causal graph."""
        self.graph = nx.DiGraph()
        self.edges: List[CausalEdge] = []
        self.roots: Set[Variable] = set()
        self.root_reasoning: Dict[Variable, str] = {}
        self.uncertain_roots: Dict[Variable, float] = {}
        self.rejected_edges: List[Tuple[CausalEdge, str]] = []
        self.deferred_edges: List[Tuple[CausalEdge, str]] = []
        self.visited: Set[Variable] = set()
    
    def add_edge(
        self,
        source: Variable,
        target: Variable,
        confidence: float,
        mechanism: str,
        evidence: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        notes: Optional[str] = None
    ):
        """
        Add a causal edge to the graph.
        
        Args:
            source: Source variable (cause)
            target: Target variable (effect)
            confidence: Confidence score (0-1)
            mechanism: Description of causal mechanism
            evidence: Optional statistical evidence
            timestamp: When edge was added
            notes: Additional notes
        """
        edge = CausalEdge(
            source=source,
            target=target,
            confidence=confidence,
            mechanism=mechanism,
            evidence=evidence,
            timestamp=timestamp or datetime.now()
        )
        
        if notes:
            edge.uncertainty_reason = notes
        
        self.edges.append(edge)
        
        # Add to NetworkX graph
        self.graph.add_node(source.name, variable=source)
        self.graph.add_node(target.name, variable=target)
        self.graph.add_edge(
            source.name,
            target.name,
            confidence=confidence,
            mechanism=mechanism,
            edge_obj=edge
        )
    
    def mark_as_root(self, variable: Variable, reasoning: str):
        """Mark a variable as a root cause."""
        self.roots.add(variable)
        self.root_reasoning[variable] = reasoning
        self.graph.add_node(variable.name, variable=variable, is_root=True)
    
    def add_uncertain_root(self, variable: Variable, confidence: float):
        """Add a variable as an uncertain root."""
        self.uncertain_roots[variable] = confidence
    
    def add_rejected_edge(self, edge: CausalEdge, reason: str):
        """Record a rejected edge."""
        self.rejected_edges.append((edge, reason))
    
    def add_deferred_edge(self, edge: CausalEdge, reason: str):
        """Add an edge to the deferred list."""
        self.deferred_edges.append((edge, reason))
    
    def get_deferred_edges(self) -> List[Tuple[CausalEdge, str]]:
        """Get all deferred edges."""
        return self.deferred_edges
    
    def mark_visited(self, variable: Variable):
        """Mark a variable as visited."""
        self.visited.add(variable)
    
    def is_visited(self, variable: Variable) -> bool:
        """Check if variable has been visited."""
        return variable in self.visited
    
    def get_roots(self) -> List[Variable]:
        """Get all root variables."""
        return list(self.roots)
    
    def get_all_variables(self) -> List[Variable]:
        """Get all variables in the graph."""
        variables = set()
        for edge in self.edges:
            variables.add(edge.source)
            variables.add(edge.target)
        variables.update(self.roots)
        return list(variables)
    
    def get_edges_from(self, variable: Variable) -> List[CausalEdge]:
        """Get all edges originating from a variable."""
        return [e for e in self.edges if e.source == variable]
    
    def get_edges_to(self, variable: Variable) -> List[CausalEdge]:
        """Get all edges pointing to a variable."""
        return [e for e in self.edges if e.target == variable]
    
    def get_parents(self, variable: Variable) -> List[Variable]:
        """Get parent variables (direct causes)."""
        return [e.source for e in self.get_edges_to(variable)]
    
    def get_children(self, variable: Variable) -> List[Variable]:
        """Get child variables (direct effects)."""
        return [e.target for e in self.get_edges_from(variable)]
    
    def get_common_parents(
        self,
        var1: Variable,
        var2: Variable
    ) -> List[Variable]:
        """Get variables that are parents of both var1 and var2."""
        parents1 = set(self.get_parents(var1))
        parents2 = set(self.get_parents(var2))
        return list(parents1.intersection(parents2))
    
    def get_path_variables(
        self,
        source: Variable,
        target: Variable
    ) -> List[Variable]:
        """Get all variables on paths between source and target."""
        if source.name not in self.graph or target.name not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph,
                source.name,
                target.name
            ))
            
            path_vars = set()
            for path in paths:
                for node_name in path[1:-1]:  # Exclude source and target
                    node_data = self.graph.nodes[node_name]
                    if 'variable' in node_data:
                        path_vars.add(node_data['variable'])
            
            return list(path_vars)
        except nx.NetworkXNoPath:
            return []
    
    def get_all_paths(self, max_length: int = 4) -> List[List[Variable]]:
        """Get all paths in the graph up to max_length."""
        all_paths = []
        
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target:
                    try:
                        paths = nx.all_simple_paths(
                            self.graph,
                            source,
                            target,
                            cutoff=max_length
                        )
                        for path in paths:
                            variables = [
                                self.graph.nodes[node]['variable']
                                for node in path
                            ]
                            all_paths.append(variables)
                    except (nx.NetworkXNoPath, KeyError):
                        continue
        
        return all_paths
    
    def has_path(self, source: Variable, target: Variable) -> bool:
        """Check if there is a path from source to target."""
        if source.name not in self.graph or target.name not in self.graph:
            return False
        return nx.has_path(self.graph, source.name, target.name)
    
    def would_create_cycle(self, source: Variable, target: Variable) -> bool:
        """Check if adding an edge would create a cycle."""
        # If target can reach source, adding source->target creates a cycle
        if target.name in self.graph and source.name in self.graph:
            return self.has_path(target, source)
        return False
    
    def get_implied_independencies(
        self,
        edge: CausalEdge
    ) -> List[Tuple[Variable, Variable, List[Variable]]]:
        """Get conditional independencies implied by graph structure."""
        # This is a simplified version - full d-separation would be more complex
        independencies = []
        
        # If X -> Y, then other variables should be independent of Y given X
        # (assuming no other paths)
        for var in self.get_all_variables():
            if var not in [edge.source, edge.target]:
                if not self.has_path(var, edge.target):
                    independencies.append((var, edge.target, [edge.source]))
        
        return independencies
    
    def get_average_confidence(self) -> float:
        """Get average confidence across all edges."""
        if not self.edges:
            return 0.0
        return sum(e.confidence for e in self.edges) / len(self.edges)
    
    def get_edges_summary(self) -> str:
        """Get a summary of existing edges."""
        if not self.edges:
            return "No edges yet"
        
        summary_lines = []
        for edge in self.edges:
            summary_lines.append(
                f"  {edge.source.name} -> {edge.target.name} "
                f"(confidence: {edge.confidence:.2f})"
            )
        return "\n".join(summary_lines)
    
    def format_edges_with_confidence(self) -> str:
        """Format edges with confidence for display."""
        if not self.edges:
            return "No edges"
        
        lines = []
        for edge in sorted(self.edges, key=lambda e: e.confidence, reverse=True):
            lines.append(
                f"{edge.source.name} -> {edge.target.name}: "
                f"{edge.confidence:.2f} ({edge.mechanism})"
            )
        return "\n".join(lines)
    
    def summarize(self) -> str:
        """Get a text summary of the graph."""
        summary = f"Causal Graph Summary:\n"
        summary += f"  Variables: {len(self.get_all_variables())}\n"
        summary += f"  Edges: {len(self.edges)}\n"
        summary += f"  Root causes: {len(self.roots)}\n"
        summary += f"  Average confidence: {self.get_average_confidence():.2f}\n"
        
        if self.roots:
            summary += f"\nRoot Causes:\n"
            for root in self.roots:
                summary += f"  - {root.name}\n"
        
        if self.edges:
            summary += f"\nCausal Relationships:\n"
            summary += self.get_edges_summary()
        
        return summary
    
    def visualize(
        self,
        filename: Optional[str] = None,
        show: bool = False,
        figsize: Tuple[int, int] = (12, 8)
    ):
        """
        Visualize the causal graph.
        
        Args:
            filename: Save to file if provided
            show: Display interactively if True
            figsize: Figure size
        """
        if not self.edges and not self.roots:
            print("Graph is empty, nothing to visualize")
            return
        
        plt.figure(figsize=figsize)
        
        # Use hierarchical layout
        try:
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
        except:
            pos = nx.shell_layout(self.graph)
        
        # Draw nodes
        node_colors = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            if node_data.get('is_root', False):
                node_colors.append('lightgreen')
            else:
                node_colors.append('lightblue')
        
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color=node_colors,
            node_size=2000,
            alpha=0.9
        )
        
        # Draw edges with varying thickness based on confidence
        for edge in self.edges:
            nx.draw_networkx_edges(
                self.graph,
                pos,
                [(edge.source.name, edge.target.name)],
                width=edge.confidence * 3,
                alpha=0.6,
                edge_color='gray',
                arrowsize=20,
                arrowstyle='->'
            )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            font_size=10,
            font_weight='bold'
        )
        
        # Add edge labels with confidence
        edge_labels = {
            (e.source.name, e.target.name): f"{e.confidence:.2f}"
            for e in self.edges
        }
        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels,
            font_size=8
        )
        
        plt.title("Causal Graph", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Graph saved to {filename}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary representation."""
        return {
            'variables': [
                {'name': v.name, 'description': v.description}
                for v in self.get_all_variables()
            ],
            'edges': [
                {
                    'source': e.source.name,
                    'target': e.target.name,
                    'confidence': e.confidence,
                    'mechanism': e.mechanism
                }
                for e in self.edges
            ],
            'roots': [v.name for v in self.roots],
            'statistics': {
                'n_variables': len(self.get_all_variables()),
                'n_edges': len(self.edges),
                'n_roots': len(self.roots),
                'avg_confidence': self.get_average_confidence()
            }
        }
    
    def apply_resolutions(self, resolutions: List[Any]):
        """Apply conflict resolutions to the graph."""
        for resolution in resolutions:
            if resolution.decision == 'ADD':
                self.add_edge(
                    source=resolution.edge.source,
                    target=resolution.edge.target,
                    confidence=resolution.revised_confidence,
                    mechanism=resolution.edge.mechanism,
                    notes=resolution.explanation
                )
            elif resolution.decision == 'REJECT':
                self.add_rejected_edge(
                    resolution.edge,
                    resolution.explanation
                )
        
        # Clear deferred edges after resolution
        self.deferred_edges = []


"""
Hybrid Causal Discovery System

A system that combines LLM knowledge extraction with statistical analysis
to discover causal relationships.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, CausalEdge, DiscoveryConfig

__all__ = [
    "HybridCausalDiscovery",
    "Variable",
    "CausalEdge",
    "DiscoveryConfig",
]


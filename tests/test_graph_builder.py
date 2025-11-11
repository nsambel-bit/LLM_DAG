"""Tests for the graph builder module."""

import pytest
from unittest.mock import Mock, MagicMock
from src.modules.graph_builder import ConfidentGraphBuilder
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.models.data_structures import Variable, CausalEdge, RootNode


class TestConfidentGraphBuilder:
    """Test suite for ConfidentGraphBuilder."""
    
    @pytest.fixture
    def mock_knowledge(self):
        """Create mock knowledge extractor."""
        knowledge = Mock(spec=KnowledgeExtractor)
        
        # Mock identify_root_causes
        knowledge.identify_root_causes.return_value = [
            RootNode(
                variable=Variable(name="Smoking", description="Test"),
                confidence=0.8,
                reasoning="Test reasoning"
            )
        ]
        
        # Mock expand_node
        knowledge.expand_node.return_value = [
            CausalEdge(
                source=Variable(name="Smoking", description="Test"),
                target=Variable(name="BMI", description="Test"),
                confidence=0.7,
                mechanism="Test mechanism"
            )
        ]
        
        return knowledge
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables."""
        return [
            Variable(name="Smoking", description="Number of cigarettes per day"),
            Variable(name="Exercise", description="Hours of exercise per week"),
            Variable(name="BMI", description="Body Mass Index"),
        ]
    
    @pytest.fixture
    def builder(self, mock_knowledge):
        """Create graph builder with mock knowledge."""
        return ConfidentGraphBuilder(mock_knowledge)
    
    def test_init(self, mock_knowledge):
        """Test initialization."""
        builder = ConfidentGraphBuilder(mock_knowledge, statistical_analyzer=None)
        assert builder.knowledge == mock_knowledge
        assert builder.stats is None
        assert builder.graph is not None
    
    def test_discover(self, builder, sample_variables):
        """Test graph discovery."""
        graph = builder.discover(sample_variables)
        
        assert graph is not None
        assert len(graph.get_roots()) > 0
    
    def test_creates_cycle(self, builder):
        """Test cycle detection."""
        var1 = Variable(name="A", description="Test")
        var2 = Variable(name="B", description="Test")
        
        # Add edge A -> B
        builder.graph.add_edge(var1, var2, 0.8, "test")
        
        # Check if B -> A would create cycle
        edge = CausalEdge(var2, var1, 0.8, "test")
        assert builder._creates_cycle(edge) is True
        
        # Check if A -> C would not create cycle
        var3 = Variable(name="C", description="Test")
        edge2 = CausalEdge(var1, var3, 0.8, "test")
        assert builder._creates_cycle(edge2) is False
    
    def test_compute_combined_confidence_no_stats(self, builder):
        """Test combined confidence without statistical data."""
        edge = CausalEdge(
            Variable(name="A", description="Test"),
            Variable(name="B", description="Test"),
            0.8,
            "test"
        )
        
        conf = builder._compute_combined_confidence(edge)
        assert conf == 0.8  # Should return LLM confidence when no stats


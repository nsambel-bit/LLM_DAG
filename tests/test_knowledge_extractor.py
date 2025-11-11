"""Tests for the knowledge extractor module."""

import pytest
from unittest.mock import Mock, MagicMock
from src.modules.knowledge_extractor import KnowledgeExtractor
from src.models.data_structures import Variable, GraphContext
from src.core.causal_graph import CausalGraph


class TestKnowledgeExtractor:
    """Test suite for KnowledgeExtractor."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM client."""
        llm = Mock()
        llm.complete = MagicMock()
        return llm
    
    @pytest.fixture
    def extractor(self, mock_llm):
        """Create knowledge extractor with mock LLM."""
        return KnowledgeExtractor(mock_llm, temperature=0.3, n_samples=3)
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables for testing."""
        return [
            Variable(name="Smoking", description="Number of cigarettes per day"),
            Variable(name="Exercise", description="Hours of exercise per week"),
            Variable(name="BMI", description="Body Mass Index"),
        ]
    
    def test_init(self, mock_llm):
        """Test initialization."""
        extractor = KnowledgeExtractor(mock_llm, temperature=0.5, n_samples=10)
        assert extractor.llm == mock_llm
        assert extractor.temperature == 0.5
        assert extractor.n_samples == 10
    
    def test_identify_root_causes(self, extractor, mock_llm, sample_variables):
        """Test root cause identification."""
        # Mock LLM responses
        mock_llm.complete.return_value = """
        <reasoning>
        Smoking and Exercise are not caused by other variables.
        </reasoning>
        <root_causes>
        Smoking
        Exercise
        </root_causes>
        """
        
        roots = extractor.identify_root_causes(sample_variables)
        
        assert len(roots) > 0
        assert mock_llm.complete.call_count == 3  # n_samples
    
    def test_expand_node(self, extractor, mock_llm, sample_variables):
        """Test node expansion."""
        mock_llm.complete.return_value = """
        <analysis>
        Smoking affects BMI through metabolism.
        </analysis>
        <direct_effects>
        Variable: BMI
        Confidence: 0.8
        Mechanism: Increases metabolism and affects weight
        </direct_effects>
        """
        
        graph = CausalGraph()
        context = GraphContext(all_variables=sample_variables)
        
        edges = extractor.expand_node(sample_variables[0], graph, context)
        
        assert isinstance(edges, list)
        assert mock_llm.complete.call_count > 0
    
    def test_parse_roots(self, extractor):
        """Test parsing root causes from response."""
        response = """
        <reasoning>Some reasoning</reasoning>
        <root_causes>
        Smoking
        Exercise
        </root_causes>
        """
        
        roots = extractor._parse_roots(response)
        
        assert len(roots) == 2
        assert "Smoking" in roots
        assert "Exercise" in roots
    
    def test_parse_edges(self, extractor, sample_variables):
        """Test parsing edges from response."""
        response = """
        <direct_effects>
        Variable: BMI
        Confidence: 0.8
        Mechanism: Test mechanism
        ---
        Variable: Exercise
        Confidence: 0.6
        Mechanism: Another mechanism
        </direct_effects>
        """
        
        edges = extractor._parse_edges(response, sample_variables)
        
        assert len(edges) == 2
        assert edges[0][1] == 0.8  # First confidence
        assert edges[1][1] == 0.6  # Second confidence


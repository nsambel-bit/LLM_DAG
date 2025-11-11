"""Integration tests for the full system."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig


class TestIntegration:
    """Integration tests for the complete discovery system."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM client."""
        llm = Mock()
        
        # Mock root identification
        def root_response(prompt, **kwargs):
            if "ROOT CAUSES" in prompt:
                return """
                <reasoning>
                Smoking and Exercise are external factors.
                </reasoning>
                <root_causes>
                Smoking
                Exercise
                </root_causes>
                """
            elif "direct_effects" in prompt.lower() or "DIRECTLY caused" in prompt:
                return """
                <analysis>
                This variable affects BMI.
                </analysis>
                <direct_effects>
                Variable: BMI
                Confidence: 0.75
                Mechanism: Affects body composition
                </direct_effects>
                """
            elif "plausibility" in prompt.lower():
                return """
                <plausibility>0.8</plausibility>
                <reasoning>This chain makes sense</reasoning>
                """
            else:
                return """
                <decision>ADD</decision>
                <confidence>0.7</confidence>
                <explanation>This relationship is plausible</explanation>
                <alternative>None</alternative>
                """
        
        llm.complete = MagicMock(side_effect=root_response)
        return llm
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables."""
        return [
            Variable(name="Smoking", description="Number of cigarettes per day"),
            Variable(name="Exercise", description="Hours of exercise per week"),
            Variable(name="BMI", description="Body Mass Index"),
        ]
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        n = 100
        
        smoking = np.random.normal(10, 5, n)
        exercise = np.random.normal(5, 2, n)
        bmi = 25 + 0.3 * smoking - 0.5 * exercise + np.random.normal(0, 2, n)
        
        return pd.DataFrame({
            'Smoking': smoking,
            'Exercise': exercise,
            'BMI': bmi
        })
    
    def test_discovery_without_data(self, mock_llm, sample_variables):
        """Test discovery without observational data."""
        discovery = HybridCausalDiscovery(mock_llm)
        
        config = DiscoveryConfig(
            resolve_conflicts=False,
            iterative_refinement=False,
            n_samples=2  # Reduce for testing
        )
        
        result = discovery.discover(sample_variables, data=None, config=config)
        
        assert result is not None
        assert result.graph is not None
        assert result.report is not None
        assert result.validation is not None
    
    def test_discovery_with_data(self, mock_llm, sample_variables, sample_data):
        """Test discovery with observational data."""
        discovery = HybridCausalDiscovery(mock_llm)
        
        config = DiscoveryConfig(
            resolve_conflicts=True,
            iterative_refinement=False,
            n_samples=2  # Reduce for testing
        )
        
        result = discovery.discover(sample_variables, data=sample_data, config=config)
        
        assert result is not None
        assert result.graph is not None
        assert len(result.graph.edges) >= 0
        assert result.report.sections['summary']['has_data'] is True
    
    def test_explain_graph(self, mock_llm, sample_variables):
        """Test graph explanation generation."""
        mock_llm.complete.return_value = "This is a test explanation of the causal graph."
        
        discovery = HybridCausalDiscovery(mock_llm)
        config = DiscoveryConfig(n_samples=2)
        
        result = discovery.discover(sample_variables, config=config)
        explanation = discovery.explain_graph(result.graph)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_report_generation(self, mock_llm, sample_variables):
        """Test that report contains expected sections."""
        discovery = HybridCausalDiscovery(mock_llm)
        config = DiscoveryConfig(n_samples=2)
        
        result = discovery.discover(sample_variables, config=config)
        
        assert 'summary' in result.report.sections
        assert 'variables' in result.report.sections
        assert 'edges' in result.report.sections
        assert 'validation' in result.report.sections
        
        summary = result.report.sections['summary']
        assert summary['n_variables'] == 3
        assert 'n_edges' in summary


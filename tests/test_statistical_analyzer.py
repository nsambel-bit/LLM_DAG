"""Tests for the statistical analyzer module."""

import pytest
import pandas as pd
import numpy as np
from src.modules.statistical_analyzer import StatisticalAnalyzer
from src.models.data_structures import Variable


class TestStatisticalAnalyzer:
    """Test suite for StatisticalAnalyzer."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        n = 100
        
        # Create synthetic data with known relationships
        smoking = np.random.normal(10, 5, n)
        exercise = np.random.normal(5, 2, n)
        bmi = 25 + 0.3 * smoking - 0.5 * exercise + np.random.normal(0, 2, n)
        
        return pd.DataFrame({
            'Smoking': smoking,
            'Exercise': exercise,
            'BMI': bmi
        })
    
    @pytest.fixture
    def sample_variables(self):
        """Create sample variables."""
        return [
            Variable(name="Smoking", description="Number of cigarettes per day"),
            Variable(name="Exercise", description="Hours of exercise per week"),
            Variable(name="BMI", description="Body Mass Index"),
        ]
    
    @pytest.fixture
    def analyzer(self, sample_data):
        """Create statistical analyzer with sample data."""
        return StatisticalAnalyzer(sample_data, significance_level=0.05)
    
    def test_init(self, sample_data):
        """Test initialization."""
        analyzer = StatisticalAnalyzer(sample_data, significance_level=0.01)
        assert analyzer.alpha == 0.01
        assert len(analyzer.data) == 100
    
    def test_pearson_correlation(self, analyzer, sample_variables):
        """Test Pearson correlation computation."""
        corr = analyzer._pearson_correlation(
            sample_variables[0],  # Smoking
            sample_variables[2]   # BMI
        )
        
        assert isinstance(corr, float)
        assert -1 <= corr <= 1
        assert corr > 0  # Should be positive based on our data generation
    
    def test_spearman_correlation(self, analyzer, sample_variables):
        """Test Spearman correlation computation."""
        corr = analyzer._spearman_correlation(
            sample_variables[0],  # Smoking
            sample_variables[2]   # BMI
        )
        
        assert isinstance(corr, float)
        assert -1 <= corr <= 1
    
    def test_compute_evidence_profile(self, analyzer, sample_variables):
        """Test evidence profile computation."""
        profile = analyzer.compute_evidence_profile(
            sample_variables[0],  # Smoking
            sample_variables[2]   # BMI
        )
        
        assert profile.source == sample_variables[0]
        assert profile.target == sample_variables[2]
        assert profile.correlation != 0
        assert profile.rank_correlation != 0
    
    def test_estimate_intervention_effect(self, analyzer, sample_variables):
        """Test intervention effect estimation."""
        effect = analyzer._estimate_intervention_effect(
            sample_variables[0],  # Smoking
            sample_variables[2]   # BMI
        )
        
        assert effect is not None
        assert hasattr(effect, 'coefficient')
        assert hasattr(effect, 'ci_lower')
        assert hasattr(effect, 'ci_upper')
        assert effect.coefficient > 0  # Should be positive
    
    def test_analyze_distribution(self, analyzer, sample_variables):
        """Test distribution analysis."""
        dist = analyzer._analyze_distribution(sample_variables[0])
        
        assert hasattr(dist, 'mean')
        assert hasattr(dist, 'std')
        assert hasattr(dist, 'skewness')
        assert hasattr(dist, 'kurtosis')
        assert dist.std > 0
    
    def test_interpret_correlation(self, analyzer):
        """Test correlation interpretation."""
        assert "Strong" in analyzer._interpret_correlation(0.8)
        assert "Moderate" in analyzer._interpret_correlation(0.5)
        assert "Weak" in analyzer._interpret_correlation(0.25)
        assert "Very weak" in analyzer._interpret_correlation(0.05)


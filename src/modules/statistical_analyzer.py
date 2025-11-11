"""Statistical analysis of observational data for causal inference."""

import numpy as np
import pandas as pd
from typing import List, Optional, Dict
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
import warnings

from src.models.data_structures import (
    Variable,
    CausalEdge,
    EvidenceProfile,
    Compatibility,
    Signal,
    ConditioningSet,
    GrangerResult,
    InterventionEffect,
    DistributionAnalysis,
    ConditionalIndependenceTest,
)
from src.core.causal_graph import CausalGraph

warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """
    Compute statistical evidence for causal relationships from observational data.
    """
    
    def __init__(self, data: pd.DataFrame, significance_level: float = 0.05):
        """
        Initialize statistical analyzer.
        
        Args:
            data: Observational data (variables as columns)
            significance_level: Significance level for hypothesis tests
        """
        self.data = data
        self.alpha = significance_level
        self.cache = {}  # Cache expensive computations
    
    def compute_evidence_profile(
        self,
        source: Variable,
        target: Variable,
        conditioning_set: Optional[List[Variable]] = None
    ) -> EvidenceProfile:
        """
        Comprehensive statistical analysis of potential causal relationship.
        
        Args:
            source: Source variable (potential cause)
            target: Target variable (potential effect)
            conditioning_set: Variables to condition on
            
        Returns:
            Evidence profile with multiple statistical measures
        """
        profile = EvidenceProfile(source=source, target=target)
        
        # Check if variables exist in data
        if source.name not in self.data.columns or target.name not in self.data.columns:
            return profile
        
        # 1. Correlation Analysis
        profile.correlation = self._pearson_correlation(source, target)
        profile.rank_correlation = self._spearman_correlation(source, target)
        
        # 2. Conditional Independence
        if conditioning_set:
            profile.partial_correlation = self._partial_correlation(
                source, target, conditioning_set
            )
            profile.cond_independence_test = self._test_independence(
                source, target, conditioning_set
            )
        
        # 3. Mutual Information
        profile.mutual_information = self._mutual_information(source, target)
        
        # 4. Temporal Analysis (if possible)
        if self._has_temporal_data():
            profile.granger_causality = self._granger_test(source, target)
            profile.time_lagged_correlation = self._cross_correlation(source, target)
        
        # 5. Distance Correlation
        try:
            import dcor
            profile.dcor = self._distance_correlation(source, target)
        except ImportError:
            profile.dcor = None
        
        # 6. Distributional Analysis
        profile.source_dist = self._analyze_distribution(source)
        profile.target_dist = self._analyze_distribution(target)
        profile.joint_pattern = self._analyze_joint_pattern(source, target)
        
        # 7. Intervention Effect Estimation
        profile.intervention_effect = self._estimate_intervention_effect(source, target)
        
        return profile
    
    def test_edge_compatibility(
        self,
        edge: CausalEdge,
        evidence: EvidenceProfile
    ) -> Compatibility:
        """
        Test if proposed edge is compatible with statistical evidence.
        
        Args:
            edge: Proposed causal edge
            evidence: Statistical evidence
            
        Returns:
            Compatibility assessment
        """
        signals = []
        
        # Signal 1: Correlation check
        if abs(evidence.correlation) < 0.05:
            signals.append(Signal(
                type='weak_correlation',
                severity='warning',
                message=f'Very weak correlation ({evidence.correlation:.3f})'
            ))
        
        # Signal 2: Conditional independence
        if evidence.cond_independence_test:
            if evidence.cond_independence_test.independent:
                signals.append(Signal(
                    type='conditional_independence',
                    severity='strong_conflict',
                    message='Variables are conditionally independent',
                    p_value=evidence.cond_independence_test.p_value
                ))
        
        # Signal 3: Temporal ordering
        if evidence.granger_causality:
            if evidence.granger_causality.reverse_direction:
                signals.append(Signal(
                    type='reverse_causality',
                    severity='strong_conflict',
                    message='Granger test suggests reverse direction'
                ))
        
        # Signal 4: Effect size
        if evidence.intervention_effect:
            if abs(evidence.intervention_effect.coefficient) < 0.01:
                signals.append(Signal(
                    type='negligible_effect',
                    severity='warning',
                    message='Estimated causal effect is very small'
                ))
        
        return Compatibility(
            compatible=self._assess_compatibility(signals),
            signals=signals,
            evidence=evidence
        )
    
    def suggest_conditioning_sets(
        self,
        source: Variable,
        target: Variable,
        graph: CausalGraph
    ) -> List[ConditioningSet]:
        """
        Suggest what to condition on for independence tests.
        
        Args:
            source: Source variable
            target: Target variable
            graph: Current causal graph
            
        Returns:
            List of suggested conditioning sets
        """
        candidates = []
        
        # Strategy 1: Common parents
        common_parents = graph.get_common_parents(source, target)
        if common_parents:
            candidates.append(ConditioningSet(
                variables=common_parents,
                rationale='Common parents (potential confounders)',
                priority='high'
            ))
        
        # Strategy 2: Mediators
        mediators = graph.get_path_variables(source, target)
        if mediators:
            candidates.append(ConditioningSet(
                variables=mediators,
                rationale='Potential mediators',
                priority='medium'
            ))
        
        # Strategy 3: Highly correlated with both
        corr_candidates = self._find_correlated_variables(source, target)
        if corr_candidates:
            candidates.append(ConditioningSet(
                variables=corr_candidates,
                rationale='Strong correlation with both variables',
                priority='medium'
            ))
        
        return candidates
    
    def generate_statistical_narrative(
        self,
        source: Variable,
        target: Variable,
        evidence: EvidenceProfile
    ) -> str:
        """
        Create human-readable summary of statistical evidence.
        
        Args:
            source: Source variable
            target: Target variable
            evidence: Evidence profile
            
        Returns:
            Narrative description
        """
        narrative = f"""Statistical Evidence for {source.name} -> {target.name}:

Correlation Analysis:
- Pearson correlation: {evidence.correlation:.3f}
- Spearman correlation: {evidence.rank_correlation:.3f}
- Interpretation: {self._interpret_correlation(evidence.correlation)}

"""
        
        if evidence.partial_correlation:
            narrative += f"""Conditional Analysis:
- Partial correlation: {evidence.partial_correlation:.3f}
- Interpretation: {self._interpret_conditional(evidence)}

"""
        
        if evidence.granger_causality:
            narrative += f"""Temporal Analysis:
- Granger causality ({source.name}->{target.name}): p={min(evidence.granger_causality.forward_pvalues):.4f}
- Reverse direction: p={min(evidence.granger_causality.reverse_pvalues):.4f}
- Interpretation: {self._interpret_granger(evidence.granger_causality)}

"""
        
        if evidence.intervention_effect:
            narrative += f"""Effect Estimation:
- Estimated causal effect: {evidence.intervention_effect.coefficient:.3f}
- 95% CI: [{evidence.intervention_effect.ci_lower:.3f}, {evidence.intervention_effect.ci_upper:.3f}]
- Interpretation: {self._interpret_effect(evidence.intervention_effect)}
"""
        
        return narrative
    
    # ========== Helper Methods ==========
    
    def _pearson_correlation(self, var1: Variable, var2: Variable) -> float:
        """Compute Pearson correlation."""
        try:
            x = self.data[var1.name].dropna()
            y = self.data[var2.name].dropna()
            
            # Align indices
            common_idx = x.index.intersection(y.index)
            x = x.loc[common_idx]
            y = y.loc[common_idx]
            
            if len(x) < 3:
                return 0.0
            
            corr, _ = pearsonr(x, y)
            return corr if not np.isnan(corr) else 0.0
        except:
            return 0.0
    
    def _spearman_correlation(self, var1: Variable, var2: Variable) -> float:
        """Compute Spearman rank correlation."""
        try:
            x = self.data[var1.name].dropna()
            y = self.data[var2.name].dropna()
            
            common_idx = x.index.intersection(y.index)
            x = x.loc[common_idx]
            y = y.loc[common_idx]
            
            if len(x) < 3:
                return 0.0
            
            corr, _ = spearmanr(x, y)
            return corr if not np.isnan(corr) else 0.0
        except:
            return 0.0
    
    def _partial_correlation(
        self,
        var1: Variable,
        var2: Variable,
        conditioning_set: List[Variable]
    ) -> float:
        """Compute partial correlation controlling for conditioning set."""
        try:
            # Get data
            y = self.data[var2.name].values
            x = self.data[var1.name].values
            z = self.data[[v.name for v in conditioning_set]].values
            
            # Regress y and x on z
            model_y = LinearRegression().fit(z, y)
            model_x = LinearRegression().fit(z, x)
            
            # Get residuals
            resid_y = y - model_y.predict(z)
            resid_x = x - model_x.predict(z)
            
            # Correlation of residuals
            corr, _ = pearsonr(resid_x, resid_y)
            return corr if not np.isnan(corr) else 0.0
        except:
            return 0.0
    
    def _test_independence(
        self,
        var1: Variable,
        var2: Variable,
        conditioning_set: List[Variable]
    ) -> ConditionalIndependenceTest:
        """Test conditional independence."""
        try:
            partial_corr = self._partial_correlation(var1, var2, conditioning_set)
            n = len(self.data)
            k = len(conditioning_set)
            
            # Fisher's z-transformation
            z = 0.5 * np.log((1 + partial_corr) / (1 - partial_corr))
            se = 1 / np.sqrt(n - k - 3)
            test_stat = z / se
            p_value = 2 * (1 - stats.norm.cdf(abs(test_stat)))
            
            return ConditionalIndependenceTest(
                independent=(p_value > self.alpha),
                p_value=p_value,
                test_statistic=test_stat,
                summary=f"p={p_value:.4f}, {'independent' if p_value > self.alpha else 'dependent'}"
            )
        except:
            return ConditionalIndependenceTest(
                independent=False,
                p_value=1.0,
                test_statistic=0.0,
                summary="Test failed"
            )
    
    def _mutual_information(self, var1: Variable, var2: Variable) -> float:
        """Compute mutual information."""
        try:
            from sklearn.metrics import mutual_info_score
            from sklearn.preprocessing import KBinsDiscretizer
            
            x = self.data[var1.name].values.reshape(-1, 1)
            y = self.data[var2.name].values.reshape(-1, 1)
            
            # Discretize continuous variables
            est = KBinsDiscretizer(n_bins=10, encode='ordinal', strategy='quantile')
            x_discrete = est.fit_transform(x).ravel()
            y_discrete = est.fit_transform(y).ravel()
            
            mi = mutual_info_score(x_discrete, y_discrete)
            return mi
        except:
            return 0.0
    
    def _has_temporal_data(self) -> bool:
        """Check if data has temporal structure."""
        # Simple heuristic: check if index is datetime or if data is ordered
        return isinstance(self.data.index, pd.DatetimeIndex) or len(self.data) > 20
    
    def _granger_test(self, source: Variable, target: Variable) -> Optional[GrangerResult]:
        """Test if source Granger-causes target."""
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            
            # Prepare data
            ts_data = pd.DataFrame({
                'target': self.data[target.name],
                'source': self.data[source.name]
            }).dropna()
            
            if len(ts_data) < 20:
                return None
            
            # Test multiple lags
            max_lag = min(10, len(ts_data) // 10)
            if max_lag < 2:
                return None
            
            results = grangercausalitytests(ts_data, max_lag, verbose=False)
            
            # Test reverse direction
            ts_data_reverse = ts_data[['source', 'target']].rename(
                columns={'source': 'target', 'target': 'source'}
            )
            results_reverse = grangercausalitytests(ts_data_reverse, max_lag, verbose=False)
            
            forward_pvals = [r[0]['ssr_ftest'][1] for r in results.values()]
            reverse_pvals = [r[0]['ssr_ftest'][1] for r in results_reverse.values()]
            
            return GrangerResult(
                forward_pvalues=forward_pvals,
                reverse_pvalues=reverse_pvals,
                optimal_lag=np.argmin(forward_pvals) + 1,
                forward_significant=min(forward_pvals) < self.alpha,
                reverse_direction=min(reverse_pvals) < self.alpha
            )
        except:
            return None
    
    def _cross_correlation(
        self,
        source: Variable,
        target: Variable,
        max_lag: int = 10
    ) -> Dict:
        """Compute cross-correlation at different lags."""
        try:
            x = self.data[source.name].values
            y = self.data[target.name].values
            
            correlations = {}
            for lag in range(max_lag + 1):
                if lag == 0:
                    corr = np.corrcoef(x, y)[0, 1]
                else:
                    corr = np.corrcoef(x[:-lag], y[lag:])[0, 1]
                correlations[f'lag_{lag}'] = corr
            
            return correlations
        except:
            return {}
    
    def _distance_correlation(self, var1: Variable, var2: Variable) -> float:
        """Compute distance correlation."""
        try:
            import dcor
            x = self.data[var1.name].values
            y = self.data[var2.name].values
            return dcor.distance_correlation(x, y)
        except:
            return 0.0
    
    def _analyze_distribution(self, variable: Variable) -> DistributionAnalysis:
        """Analyze variable distribution."""
        try:
            data = self.data[variable.name].dropna()
            
            return DistributionAnalysis(
                mean=float(data.mean()),
                std=float(data.std()),
                skewness=float(data.skew()),
                kurtosis=float(data.kurtosis()),
                distribution_type=self._infer_distribution_type(data)
            )
        except:
            return DistributionAnalysis(
                mean=0.0, std=0.0, skewness=0.0, kurtosis=0.0,
                distribution_type='unknown'
            )
    
    def _infer_distribution_type(self, data: pd.Series) -> str:
        """Infer distribution type."""
        # Simple heuristic based on skewness and kurtosis
        skew = data.skew()
        kurt = data.kurtosis()
        
        if abs(skew) < 0.5 and abs(kurt) < 1:
            return 'normal'
        elif skew > 1:
            return 'right_skewed'
        elif skew < -1:
            return 'left_skewed'
        else:
            return 'other'
    
    def _analyze_joint_pattern(self, var1: Variable, var2: Variable) -> str:
        """Analyze joint distribution pattern."""
        try:
            corr = self._pearson_correlation(var1, var2)
            
            if abs(corr) > 0.7:
                return 'strong_linear'
            elif abs(corr) > 0.4:
                return 'moderate_linear'
            else:
                return 'weak_or_nonlinear'
        except:
            return 'unknown'
    
    def _estimate_intervention_effect(
        self,
        source: Variable,
        target: Variable
    ) -> Optional[InterventionEffect]:
        """Estimate causal effect using regression."""
        try:
            X = self.data[[source.name]].values
            y = self.data[target.name].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            coef = model.coef_[0]
            
            # Estimate confidence interval (simplified)
            predictions = model.predict(X)
            residuals = y - predictions
            std_error = np.std(residuals) / np.sqrt(len(y))
            
            ci_lower = coef - 1.96 * std_error
            ci_upper = coef + 1.96 * std_error
            
            # Simple t-test for significance
            t_stat = coef / std_error
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(y) - 2))
            
            return InterventionEffect(
                coefficient=coef,
                ci_lower=ci_lower,
                ci_upper=ci_upper,
                p_value=p_value
            )
        except:
            return None
    
    def _find_correlated_variables(
        self,
        var1: Variable,
        var2: Variable,
        threshold: float = 0.3
    ) -> List[Variable]:
        """Find variables correlated with both var1 and var2."""
        candidates = []
        
        for col in self.data.columns:
            if col not in [var1.name, var2.name]:
                var = Variable(name=col, description='')
                corr1 = abs(self._pearson_correlation(var, var1))
                corr2 = abs(self._pearson_correlation(var, var2))
                
                if corr1 > threshold and corr2 > threshold:
                    candidates.append(var)
        
        return candidates[:5]  # Top 5
    
    def _assess_compatibility(self, signals: List[Signal]) -> bool:
        """Assess overall compatibility based on signals."""
        strong_conflicts = [s for s in signals if s.severity == 'strong_conflict']
        return len(strong_conflicts) == 0
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation strength."""
        abs_corr = abs(corr)
        if abs_corr > 0.7:
            return f"Strong {'positive' if corr > 0 else 'negative'} correlation"
        elif abs_corr > 0.4:
            return f"Moderate {'positive' if corr > 0 else 'negative'} correlation"
        elif abs_corr > 0.2:
            return f"Weak {'positive' if corr > 0 else 'negative'} correlation"
        else:
            return "Very weak or no correlation"
    
    def _interpret_conditional(self, evidence: EvidenceProfile) -> str:
        """Interpret conditional independence test."""
        if evidence.cond_independence_test:
            if evidence.cond_independence_test.independent:
                return "Variables are conditionally independent (relationship may be spurious)"
            else:
                return "Variables remain dependent after conditioning (supports causal link)"
        return "No conditional test performed"
    
    def _interpret_granger(self, result: GrangerResult) -> str:
        """Interpret Granger causality result."""
        if result.forward_significant and not result.reverse_direction:
            return "Strong support for forward causation"
        elif result.reverse_direction and not result.forward_significant:
            return "Suggests reverse causation"
        elif result.forward_significant and result.reverse_direction:
            return "Bidirectional relationship or common cause"
        else:
            return "No clear temporal precedence"
    
    def _interpret_effect(self, effect: InterventionEffect) -> str:
        """Interpret intervention effect."""
        if effect.p_value > 0.05:
            return "Effect not statistically significant"
        elif abs(effect.coefficient) > 0.5:
            return f"Large effect size (coef={effect.coefficient:.3f})"
        elif abs(effect.coefficient) > 0.2:
            return f"Moderate effect size (coef={effect.coefficient:.3f})"
        else:
            return f"Small effect size (coef={effect.coefficient:.3f})"


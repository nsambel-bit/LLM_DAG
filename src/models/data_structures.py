"""Core data structures for the causal discovery system."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class Variable:
    """Represents a variable in the causal system."""
    
    name: str
    description: str
    metadata: Dict = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name == other.name
        return False
    
    def __repr__(self):
        return f"Variable({self.name})"


@dataclass
class CausalEdge:
    """Represents a directed causal edge between two variables."""
    
    source: Variable
    target: Variable
    confidence: float
    mechanism: str
    alternative_explanations: List[str] = field(default_factory=list)
    statistical_support: Optional[float] = None
    evidence: Optional[Dict] = None
    timestamp: Optional[datetime] = None
    uncertainty_reason: Optional[str] = None
    
    def __repr__(self):
        return f"{self.source.name} -> {self.target.name} (conf={self.confidence:.2f})"


@dataclass
class RootNode:
    """Represents a potential root cause variable."""
    
    variable: Variable
    confidence: float
    reasoning: str


@dataclass
class Explanation:
    """Detailed explanation of a causal relationship."""
    
    mechanism: str
    time_scale: str
    nature: str
    potential_confounders: List[str]
    boundary_conditions: str
    confidence_level: int
    justification: str


@dataclass
class Signal:
    """A signal from statistical analysis."""
    
    type: str
    severity: str
    message: str
    p_value: Optional[float] = None


@dataclass
class GrangerResult:
    """Results from Granger causality test."""
    
    forward_pvalues: List[float]
    reverse_pvalues: List[float]
    optimal_lag: int
    forward_significant: bool
    reverse_direction: bool
    
    @property
    def summary(self):
        return f"Forward: p={min(self.forward_pvalues):.4f}, Reverse: p={min(self.reverse_pvalues):.4f}"


@dataclass
class InterventionEffect:
    """Estimated intervention effect."""
    
    coefficient: float
    ci_lower: float
    ci_upper: float
    p_value: float


@dataclass
class DistributionAnalysis:
    """Analysis of variable distribution."""
    
    mean: float
    std: float
    skewness: float
    kurtosis: float
    distribution_type: str


@dataclass
class ConditionalIndependenceTest:
    """Results of conditional independence test."""
    
    independent: bool
    p_value: float
    test_statistic: float
    summary: str


@dataclass
class EvidenceProfile:
    """Comprehensive statistical evidence for a causal relationship."""
    
    source: Variable
    target: Variable
    correlation: float = 0.0
    rank_correlation: float = 0.0
    partial_correlation: Optional[float] = None
    cond_independence_test: Optional[ConditionalIndependenceTest] = None
    mutual_information: Optional[float] = None
    granger_causality: Optional[GrangerResult] = None
    time_lagged_correlation: Optional[Dict] = None
    dcor: Optional[float] = None
    source_dist: Optional[DistributionAnalysis] = None
    target_dist: Optional[DistributionAnalysis] = None
    joint_pattern: Optional[str] = None
    intervention_effect: Optional[InterventionEffect] = None


@dataclass
class Compatibility:
    """Compatibility assessment between edge and statistical evidence."""
    
    compatible: bool
    signals: List[Signal]
    evidence: Optional[EvidenceProfile] = None


@dataclass
class ConditioningSet:
    """A set of variables to condition on."""
    
    variables: List[Variable]
    rationale: str
    priority: str


@dataclass
class EdgeDecision:
    """Decision about whether to add an edge."""
    
    edge: CausalEdge
    action: str = 'DEFER'  # ADD, DEFER, or REJECT
    reason: str = ''
    confidence: float = 0.0
    evidence: Optional[EvidenceProfile] = None


@dataclass
class Resolution:
    """Resolution of a conflicted edge."""
    
    edge: CausalEdge
    decision: str  # ADD, REJECT, or MODIFY
    revised_confidence: float
    explanation: str
    alternative_hypothesis: Optional[str] = None
    original_evidence: Optional[EvidenceProfile] = None


@dataclass
class Violation:
    """A validation violation."""
    
    type: str
    details: str
    severity: str
    edge: Optional[CausalEdge] = None
    p_value: Optional[float] = None


@dataclass
class TestResult:
    """Result of a validation test."""
    
    passed: bool
    violations: List[Any]
    score: float
    
    def __repr__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"TestResult({status}, score={self.score:.2f}, violations={len(self.violations)})"


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    
    graph: Any  # CausalGraph
    tests: Dict[str, TestResult] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_test(self, name: str, result: TestResult):
        """Add a test result."""
        self.tests[name] = result
    
    def is_satisfactory(self) -> bool:
        """Check if validation is satisfactory."""
        if not self.tests:
            return False
        return all(test.passed for test in self.tests.values())
    
    def get_issues(self) -> List[Violation]:
        """Get all validation issues."""
        issues = []
        for test_result in self.tests.values():
            issues.extend(test_result.violations)
        return issues
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'satisfactory': self.is_satisfactory(),
            'tests': {
                name: {
                    'passed': result.passed,
                    'score': result.score,
                    'n_violations': len(result.violations)
                }
                for name, result in self.tests.items()
            }
        }


@dataclass
class DiscoveryConfig:
    """Configuration for causal discovery."""
    
    resolve_conflicts: bool = True
    iterative_refinement: bool = True
    max_refinement_iterations: int = 3
    significance_level: float = 0.05
    confidence_threshold: float = 0.5
    temperature: float = 0.3
    n_samples: int = 5


@dataclass
class Report:
    """Comprehensive discovery report."""
    
    sections: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_section(self, name: str, content: Any):
        """Add a section to the report."""
        self.sections[name] = content
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'sections': self.sections
        }
    
    def save(self, filename: str):
        """Save report to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


@dataclass
class GraphContext:
    """Context for graph construction."""
    
    all_variables: List[Variable]
    visited: set = field(default_factory=set)
    
    def is_visited(self, variable: Variable) -> bool:
        """Check if variable has been visited."""
        return variable in self.visited


@dataclass
class DiscoveryResult:
    """Result of causal discovery."""
    
    graph: Any  # CausalGraph
    report: Report
    validation: ValidationReport
    
    def __repr__(self):
        return f"DiscoveryResult(edges={len(self.graph.edges)}, satisfactory={self.validation.is_satisfactory()})"


@dataclass
class Refinement:
    """A refinement to apply to the graph."""
    
    type: str  # ADD_EDGE, REMOVE_EDGE, MODIFY_CONFIDENCE
    params: Dict


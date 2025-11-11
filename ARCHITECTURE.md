# System Architecture

## Overview

The Hybrid Causal Discovery System combines Large Language Model (LLM) knowledge with statistical analysis to discover causal relationships from variable descriptions and optional observational data.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Hybrid Causal Discovery                   │
│                                                              │
│  Input: Variables + Descriptions + [Optional] Data          │
│     ↓                                                        │
│  Module 1: Knowledge Extraction (LLM)                       │
│     ↓                                                        │
│  Module 2: Statistical Analysis (if data available)         │
│     ↓                                                        │
│  Module 3: Graph Construction (BFS with confidence)         │
│     ↓                                                        │
│  Module 4: Conflict Detection & Resolution                  │
│     ↓                                                        │
│  Module 5: Validation & Refinement                          │
│     ↓                                                        │
│  Output: Causal Graph + Confidence Scores + Explanations    │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Structures (`src/models/data_structures.py`)

**Key Classes:**
- `Variable`: Represents a variable with name and description
- `CausalEdge`: Directed edge with confidence and mechanism
- `EvidenceProfile`: Statistical evidence for a relationship
- `DiscoveryConfig`: Configuration parameters
- `DiscoveryResult`: Complete discovery results

### 2. LLM Client (`src/core/llm_client.py`)

**Purpose:** Interface to OpenRouter API for LLM access

**Features:**
- Configurable model selection
- Temperature and token controls
- Error handling and retries
- Batch completion support

**Default Model:** Claude 3.5 Sonnet (anthropic/claude-3.5-sonnet)

### 3. Causal Graph (`src/core/causal_graph.py`)

**Purpose:** Store and manipulate causal graph structure

**Features:**
- DAG enforcement (cycle detection)
- Root cause tracking
- Edge confidence management
- Path analysis
- Visualization using NetworkX
- Export to multiple formats

**Key Methods:**
- `add_edge()`: Add causal relationship
- `get_parents()`: Get direct causes
- `get_children()`: Get direct effects
- `has_path()`: Check connectivity
- `visualize()`: Create graph visualization

### 4. Knowledge Extractor (`src/modules/knowledge_extractor.py`)

**Purpose:** Extract causal knowledge from LLM with uncertainty quantification

**Algorithm:**
1. **Root Identification**: Sample LLM multiple times to identify variables not caused by others
2. **Self-Consistency**: Aggregate multiple samples for confidence estimation
3. **Node Expansion**: For each node, query LLM for direct effects
4. **Mechanism Extraction**: Extract causal mechanisms and alternative explanations

**Key Parameters:**
- `temperature`: Sampling temperature (default: 0.3)
- `n_samples`: Number of samples for consistency (default: 5)

**Confidence Computation:**
```
confidence = (frequency_in_samples + avg_llm_confidence) / 2
```

### 5. Statistical Analyzer (`src/modules/statistical_analyzer.py`)

**Purpose:** Compute statistical evidence from observational data

**Statistical Tests:**
1. **Correlation Analysis**
   - Pearson correlation (linear relationships)
   - Spearman correlation (monotonic relationships)
   
2. **Conditional Independence**
   - Partial correlation
   - Fisher's z-transformation test
   
3. **Temporal Analysis** (if applicable)
   - Granger causality tests
   - Cross-correlation at multiple lags
   
4. **Effect Estimation**
   - Linear regression for effect size
   - Confidence intervals
   - Significance testing

5. **Non-linear Dependencies**
   - Mutual information
   - Distance correlation

**Evidence Profile:**
For each potential edge, generates comprehensive statistical evidence including:
- Correlation measures
- Conditional independence tests
- Temporal precedence (Granger)
- Effect size estimates
- Distribution analyses

### 6. Graph Builder (`src/modules/graph_builder.py`)

**Purpose:** Construct causal graph using BFS with confidence tracking

**Algorithm:**

```
1. Identify root causes using LLM
2. Initialize priority queue with roots (sorted by confidence)
3. While queue not empty:
   a. Dequeue highest confidence node
   b. Query LLM for direct effects
   c. For each proposed edge:
      - Check for cycles
      - Evaluate LLM confidence
      - Test statistical compatibility (if data available)
      - Compute combined confidence
      - Decide: ADD, DEFER, or REJECT
   d. Add accepted edges and targets to queue
4. Return graph with deferred edges marked
```

**Edge Decision Logic:**
- **REJECT** if creates cycle
- **DEFER** if LLM confidence < 0.3
- **DEFER** if strong statistical conflict
- **ADD** if combined confidence > 0.6
- **DEFER** otherwise

**Combined Confidence:**
```
combined = α × llm_confidence + (1-α) × statistical_confidence
where α = 0.6 (favoring domain knowledge)
```

### 7. Conflict Resolver (`src/modules/conflict_resolver.py`)

**Purpose:** Resolve conflicts between LLM knowledge and statistical evidence

**Process:**
1. Collect all deferred edges
2. For each conflict:
   a. Generate statistical narrative
   b. Present to LLM with original reasoning
   c. Ask LLM to reconsider with evidence
   d. Parse decision (ADD/REJECT/MODIFY)
3. Apply resolutions to graph

**LLM Dialogue:**
The system presents:
- Original LLM reasoning
- Statistical evidence (correlations, tests, effect sizes)
- Current graph structure
- Asks for reconciliation

### 8. Graph Validator (`src/modules/graph_validator.py`)

**Purpose:** Validate and iteratively refine discovered graph

**Validation Tests:**

1. **Structural Validity**
   - Check for root causes
   - Identify isolated nodes
   - Verify DAG property

2. **Confidence Distribution**
   - Average confidence level
   - Proportion of low-confidence edges

3. **Statistical Consistency** (with data)
   - Test implied conditional independencies
   - Compare with d-separation

4. **Logical Consistency**
   - Sample causal chains
   - Ask LLM to verify plausibility
   - Identify suspicious paths

5. **Completeness**
   - Check connectivity
   - Ensure sufficient edges

**Refinement:**
- Iteratively fix issues
- Remove very low confidence edges
- Adjust confidences based on violations
- Re-validate after changes

### 9. Main Orchestrator (`src/discovery.py`)

**Purpose:** Coordinate all modules in discovery pipeline

**Discovery Pipeline:**

```
Phase 1: Initial Graph Construction
├─ Initialize knowledge extractor
├─ Initialize statistical analyzer (if data)
└─ Run BFS graph builder

Phase 2: Conflict Resolution (if enabled)
├─ Collect deferred edges
├─ Resolve conflicts with LLM-data dialogue
└─ Apply resolutions

Phase 3: Validation
├─ Run all validation tests
└─ Generate validation report

Phase 4: Iterative Refinement (if issues found)
├─ Identify issues
├─ Propose refinements
├─ Apply changes
└─ Re-validate

Output: Graph + Report + Validation
```

## Data Flow

```
Variables (with descriptions)
    ↓
KnowledgeExtractor.identify_root_causes()
    → [Root nodes with confidence]
    ↓
GraphBuilder.discover()
    → For each root:
        → KnowledgeExtractor.expand_node()
        → [Proposed edges]
        → For each edge:
            ✓ Check cycles
            ✓ Check LLM confidence
            ✓ StatisticalAnalyzer.compute_evidence()
            ✓ Compute combined confidence
            → Decision: ADD/DEFER/REJECT
    ↓
CausalGraph (with deferred edges)
    ↓
ConflictResolver.resolve_conflicts()
    → For each deferred edge:
        → Present evidence to LLM
        → Get revised decision
    ↓
CausalGraph (conflicts resolved)
    ↓
GraphValidator.validate()
    → Run validation tests
    → Generate report
    ↓
GraphValidator.iterative_refinement() [if needed]
    → Fix issues
    → Re-validate
    ↓
Final CausalGraph + Report + Validation
```

## Design Decisions

### 1. Why BFS for Graph Construction?

- **Systematic exploration**: Ensures all variables are considered
- **Confidence-based ordering**: Explores most confident paths first
- **Acyclic enforcement**: Natural cycle prevention during construction
- **Incremental context**: Each node has partial graph context

### 2. Why Combine LLM and Statistics?

| LLM Strengths | Statistical Strengths |
|---------------|----------------------|
| Domain knowledge | Objectivity |
| Mechanism understanding | Quantitative evidence |
| Handles small/no data | Temporal ordering |
| Contextual reasoning | Effect size estimation |

**Synergy:** LLM proposes, statistics verify, conflicts are resolved through dialogue.

### 3. Why Self-Consistency Sampling?

- **Uncertainty quantification**: Multiple samples reveal uncertainty
- **Robustness**: Reduces impact of single bad sample
- **Confidence calibration**: Frequency ≈ confidence
- **Cost**: Trade-off between accuracy and API costs (default: 5 samples)

### 4. Why Confidence Weighting (60% LLM, 40% Stats)?

- **Domain knowledge priority**: Causal relationships often domain-specific
- **Small sample robustness**: Statistics unreliable with small n
- **Mechanism preservation**: Statistical correlation ≠ causation
- **Configurable**: Can be adjusted per use case

## Extension Points

### Adding New Statistical Tests

```python
# In StatisticalAnalyzer
def _my_custom_test(self, source, target):
    # Implement test
    return result

def compute_evidence_profile(self, source, target, ...):
    # Add to profile
    profile.my_test = self._my_custom_test(source, target)
```

### Custom LLM Prompts

```python
# In KnowledgeExtractor
def _build_custom_prompt(self, ...):
    return f"""
    Your custom prompt template
    """
```

### Additional Validation Tests

```python
# In GraphValidator
def _test_custom_property(self, graph):
    violations = []
    # Check custom property
    return TestResult(passed=..., violations=violations, score=...)
```

### Alternative Graph Construction

Replace `ConfidentGraphBuilder` with custom algorithm while maintaining the interface.

## Performance Considerations

### Time Complexity

- **Root identification**: O(n × k) where n=variables, k=samples
- **Graph construction**: O(n² × k) worst case (all pairs)
- **Statistical analysis**: O(m × n) where m=data samples
- **Validation**: O(e × k) where e=edges

### Space Complexity

- **Graph storage**: O(n + e)
- **Evidence profiles**: O(e × d) where d=data size
- **Cache**: O(computation results)

### Optimization Strategies

1. **Caching**: Statistical results cached by (source, target) pair
2. **Early termination**: Stop BFS if confidence too low
3. **Batch processing**: Multiple LLM calls in parallel (future)
4. **Sampling**: Validate subset of edges/paths

## Error Handling

### LLM API Failures
- Retry with exponential backoff
- Fall back to default responses
- Log failures for review

### Statistical Test Failures
- Catch exceptions per test
- Continue with other tests
- Report unavailable tests

### Invalid Configurations
- Validate inputs early
- Provide helpful error messages
- Suggest corrections

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock LLM responses
- Use synthetic data with known structure

### Integration Tests
- Test full pipeline
- Verify module interactions
- Check end-to-end results

### Validation Tests
- Compare with known causal graphs
- Test on benchmark datasets
- Measure accuracy metrics

## Future Enhancements

1. **Parallel LLM calls**: Speed up sampling
2. **Active learning**: Ask LLM targeted questions
3. **Constraint integration**: User-provided causal constraints
4. **Mechanism refinement**: Detailed mechanism extraction
5. **Counterfactual reasoning**: What-if analysis
6. **Intervention simulation**: Predict intervention effects
7. **Temporal graphs**: Time-varying causal structures
8. **Multi-modal inputs**: Images, time series, text

## References

- Pearl, J. (2009). Causality: Models, Reasoning, and Inference
- Spirtes, P., et al. (2000). Causation, Prediction, and Search
- Wang, X., et al. (2023). Large Language Models for Causal Discovery
- Granger, C. (1969). Investigating Causal Relations by Econometric Models


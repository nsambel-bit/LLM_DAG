# Tutorial: Getting Started with Hybrid Causal Discovery

This tutorial will walk you through using the Hybrid Causal Discovery System step-by-step.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Tutorial 1: Simple Discovery (No Data)](#tutorial-1-simple-discovery-no-data)
5. [Tutorial 2: Discovery with Data](#tutorial-2-discovery-with-data)
6. [Tutorial 3: Custom Configuration](#tutorial-3-custom-configuration)
7. [Tutorial 4: Working with Results](#tutorial-4-working-with-results)
8. [Tutorial 5: Advanced Usage](#tutorial-5-advanced-usage)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.8 or higher installed
- Basic understanding of Python programming
- OpenRouter API account (free tier available)
- Basic understanding of causality concepts (helpful but not required)

## Installation

### Step 1: Set Up Environment

```bash
# Navigate to project directory
cd LLM_DAG

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key (you'll need it in the next step)

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example
cp config/.env.example .env
```

Edit `.env` and add your API key:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
```

### Step 4: Verify Setup

```bash
python test_setup.py
```

You should see:
```
[SUCCESS] SETUP COMPLETE - System is ready to use!
```

---

## Basic Concepts

### What is Causal Discovery?

Causal discovery is the process of finding cause-and-effect relationships between variables. Unlike correlation, causation implies that changing one variable will change another.

**Example:**
- **Correlation**: Ice cream sales and drowning deaths are correlated
- **Causation**: Hot weather causes both (common cause)

### Key Terms

- **Variable**: A measurable quantity (e.g., "Age", "Income", "Temperature")
- **Causal Edge**: A directed relationship from cause to effect (A → B)
- **Root Cause**: A variable not caused by others in the system
- **Confidence**: How certain we are about a relationship (0-1)
- **Mechanism**: Description of HOW the cause affects the effect

### How This System Works

1. **LLM Knowledge**: Uses AI to understand domain relationships
2. **Statistical Analysis**: Tests relationships using data (if available)
3. **Conflict Resolution**: Reconciles disagreements between AI and data
4. **Validation**: Checks if discovered graph makes sense
5. **Output**: Causal graph with confidence scores and explanations

---

## Tutorial 1: Simple Discovery (No Data)

Let's start with the simplest case: discovering causal relationships using only variable descriptions.

### Example: Coffee Shop Variables

Create a new file `my_first_discovery.py`:

```python
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable
from src.core.llm_client import get_llm_client

# Step 1: Define your variables
variables = [
    Variable(
        name="Temperature",
        description="Outside temperature in degrees Celsius"
    ),
    Variable(
        name="Ice_Coffee_Sales",
        description="Number of iced coffee drinks sold per day"
    ),
    Variable(
        name="Hot_Coffee_Sales",
        description="Number of hot coffee drinks sold per day"
    ),
]

# Step 2: Initialize the system
discovery = HybridCausalDiscovery(llm_client=get_llm_client())

# Step 3: Run discovery
print("Discovering causal relationships...")
result = discovery.discover(variables)

# Step 4: View results
print(f"\nFound {len(result.graph.edges)} causal relationships:")
for edge in result.graph.edges:
    print(f"  {edge.source.name} → {edge.target.name}")
    print(f"    Confidence: {edge.confidence:.2f}")
    print(f"    Mechanism: {edge.mechanism}")

# Step 5: Save visualization
result.graph.visualize("coffee_shop_graph.png")
print("\nGraph saved to coffee_shop_graph.png")
```

Run it:
```bash
python my_first_discovery.py
```

**Expected Output:**
```
Found 2 causal relationships:
  Temperature → Ice_Coffee_Sales
    Confidence: 0.82
    Mechanism: Higher temperatures increase demand for cold beverages
  Temperature → Hot_Coffee_Sales
    Confidence: 0.78
    Mechanism: Lower temperatures increase desire for warm drinks
```

### What Just Happened?

1. **Root Identification**: System identified Temperature as a root cause
2. **Edge Discovery**: Found that Temperature affects both types of sales
3. **Confidence Scoring**: Assigned confidence based on LLM consistency
4. **Mechanism Extraction**: Explained HOW the relationships work

---

## Tutorial 2: Discovery with Data

Now let's use both LLM knowledge AND statistical data.

### Example: Health Variables

```python
import pandas as pd
import numpy as np
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig
from src.core.llm_client import get_llm_client

# Step 1: Generate or load your data
np.random.seed(42)
n = 200

# Simulate data with known causal structure:
# Smoking → Lung_Capacity
# Exercise → Lung_Capacity
smoking = np.random.poisson(5, n)
exercise = np.random.gamma(3, 1, n)
lung_capacity = (
    100 - 2 * smoking + 3 * exercise + 
    np.random.normal(0, 5, n)
)

data = pd.DataFrame({
    'Smoking': smoking,
    'Exercise': exercise,
    'Lung_Capacity': lung_capacity
})

# Step 2: Define variables
variables = [
    Variable(
        name="Smoking",
        description="Number of cigarettes smoked per day"
    ),
    Variable(
        name="Exercise",
        description="Hours of aerobic exercise per week"
    ),
    Variable(
        name="Lung_Capacity",
        description="Lung capacity in liters (vital capacity)"
    ),
]

# Step 3: Configure discovery
config = DiscoveryConfig(
    resolve_conflicts=True,  # Enable conflict resolution
    iterative_refinement=True,  # Enable refinement
    n_samples=3  # Number of LLM samples
)

# Step 4: Run discovery with data
discovery = HybridCausalDiscovery(llm_client=get_llm_client())
result = discovery.discover(variables, data=data, config=config)

# Step 5: Examine results
print("\n=== DISCOVERY RESULTS ===")
print(f"Root causes: {[r.name for r in result.graph.get_roots()]}")
print(f"Causal edges: {len(result.graph.edges)}")
print(f"Average confidence: {result.graph.get_average_confidence():.2f}")

print("\n=== RELATIONSHIPS ===")
for edge in sorted(result.graph.edges, key=lambda e: e.confidence, reverse=True):
    print(f"\n{edge.source.name} → {edge.target.name}")
    print(f"  LLM Confidence: {edge.confidence:.2f}")
    if edge.evidence:
        print(f"  Statistical Support: {edge.evidence.get('correlation', 'N/A')}")
    print(f"  Mechanism: {edge.mechanism[:80]}...")

# Step 6: Save comprehensive results
result.report.save("health_discovery_report.json")
result.graph.visualize("health_graph.png")
print("\n✓ Results saved!")
```

### What's Different?

1. **Data Integration**: System computes statistical evidence
2. **Conflict Detection**: Identifies when LLM and data disagree
3. **Conflict Resolution**: LLM reconsiders given statistical evidence
4. **Combined Confidence**: Merges LLM (60%) and statistical (40%) confidence
5. **Validation**: More thorough validation using data

---

## Tutorial 3: Custom Configuration

Fine-tune the discovery process for your specific needs.

### Configuration Options

```python
from src.models.data_structures import DiscoveryConfig

config = DiscoveryConfig(
    # Conflict resolution
    resolve_conflicts=True,  # True: resolve LLM-data conflicts
    
    # Iterative refinement
    iterative_refinement=True,  # True: refine graph after validation
    max_refinement_iterations=3,  # Max refinement rounds
    
    # Statistical parameters
    significance_level=0.05,  # P-value threshold for tests
    confidence_threshold=0.5,  # Min confidence to keep edge
    
    # LLM parameters
    temperature=0.3,  # Lower = more consistent, Higher = more creative
    n_samples=5  # More samples = more robust, but higher cost
)
```

### When to Use Each Setting

**High Quality, Higher Cost:**
```python
config = DiscoveryConfig(
    resolve_conflicts=True,
    iterative_refinement=True,
    max_refinement_iterations=5,
    n_samples=10,  # Very robust
    temperature=0.1  # Very consistent
)
```

**Fast Exploration, Lower Cost:**
```python
config = DiscoveryConfig(
    resolve_conflicts=False,
    iterative_refinement=False,
    n_samples=2,  # Quick but less robust
    temperature=0.5  # More variable
)
```

**Production Setting (Balanced):**
```python
config = DiscoveryConfig(
    resolve_conflicts=True,
    iterative_refinement=True,
    max_refinement_iterations=3,
    n_samples=5,
    temperature=0.3
)
```

---

## Tutorial 4: Working with Results

The system provides rich outputs. Let's explore them all.

### 1. Access Graph Structure

```python
# Get the discovered graph
graph = result.graph

# Root causes
roots = graph.get_roots()
print(f"Root causes: {[r.name for r in roots]}")

# All edges
for edge in graph.edges:
    print(f"{edge.source.name} → {edge.target.name}: {edge.confidence:.2f}")

# Parents and children
var = variables[0]
parents = graph.get_parents(var)
children = graph.get_children(var)
```

### 2. Explore Evidence

```python
# For each edge, examine the evidence
for edge in graph.edges:
    print(f"\n{edge.source.name} → {edge.target.name}")
    print(f"Confidence: {edge.confidence:.2f}")
    print(f"Mechanism: {edge.mechanism}")
    
    if hasattr(edge, 'alternative_explanations'):
        print(f"Alternatives: {edge.alternative_explanations}")
```

### 3. Read the Report

```python
# Access report sections
summary = result.report.sections['summary']
print(f"Variables: {summary['n_variables']}")
print(f"Edges: {summary['n_edges']}")
print(f"Average confidence: {summary['avg_confidence']:.2f}")

# Validation results
validation = result.report.sections['validation']
print(f"Validation satisfactory: {validation['satisfactory']}")

# Uncertainty analysis
uncertainty = result.report.sections['uncertainty']
print(f"Low confidence edges: {uncertainty['n_low_confidence']}")

# Save full report
result.report.save("my_report.json")
```

### 4. Generate Explanations

```python
# Get natural language explanation
explanation = discovery.explain_graph(result.graph)
print(explanation)

# Save to file
with open("explanation.txt", "w") as f:
    f.write(explanation)
```

### 5. Export for Other Tools

```python
# Export as JSON
import json
graph_dict = result.graph.to_dict()
with open("graph.json", "w") as f:
    json.dump(graph_dict, f, indent=2)

# Export edge list for R/Python analysis
import csv
with open("edges.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["source", "target", "confidence", "mechanism"])
    for edge in graph.edges:
        writer.writerow([
            edge.source.name,
            edge.target.name,
            edge.confidence,
            edge.mechanism
        ])
```

---

## Tutorial 5: Advanced Usage

### Custom Statistical Tests

Add your own statistical tests:

```python
from src.modules.statistical_analyzer import StatisticalAnalyzer

# Extend the analyzer
class MyStatisticalAnalyzer(StatisticalAnalyzer):
    def compute_evidence_profile(self, source, target, conditioning_set=None):
        # Call parent method
        profile = super().compute_evidence_profile(source, target, conditioning_set)
        
        # Add your custom test
        profile.my_custom_metric = self._my_custom_test(source, target)
        
        return profile
    
    def _my_custom_test(self, source, target):
        # Implement your test
        # For example, a custom non-linear test
        x = self.data[source.name].values
        y = self.data[target.name].values
        
        # Your analysis here
        result = ...
        
        return result
```

### Custom Prompts

Modify LLM prompts for your domain:

```python
from src.modules.knowledge_extractor import KnowledgeExtractor

class DomainKnowledgeExtractor(KnowledgeExtractor):
    def _build_root_prompt(self, variables):
        # Custom prompt for your domain
        return f"""
        You are an expert in [YOUR DOMAIN].
        
        [Your custom instructions]
        
        Variables:
        {self._format_variables(variables)}
        
        [Your specific guidelines]
        """
```

### Batch Processing

Process multiple variable sets:

```python
variable_sets = [
    [var1, var2, var3],
    [var4, var5, var6],
    [var7, var8, var9]
]

results = []
for i, variables in enumerate(variable_sets):
    print(f"Processing set {i+1}/{len(variable_sets)}...")
    result = discovery.discover(variables, data)
    results.append(result)
    
    # Save each result
    result.report.save(f"report_{i}.json")
    result.graph.visualize(f"graph_{i}.png")
```

---

## Troubleshooting

### Common Issues

**Issue 1: "API key not provided"**
```
Solution:
1. Check .env file exists in project root
2. Verify OPENROUTER_API_KEY is set
3. Make sure no typos in the key
4. Try: python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENROUTER_API_KEY'))"
```

**Issue 2: "No module named 'src'"**
```
Solution:
1. Make sure you're in the project root directory
2. Check that src/ folder exists
3. Try: python -c "import sys; print(sys.path)"
```

**Issue 3: Low confidence scores**
```
Possible causes:
1. Variable descriptions too vague → Add more detail
2. True relationship is weak → Normal behavior
3. n_samples too low → Increase to 10
4. Temperature too high → Lower to 0.1

Solution:
config = DiscoveryConfig(n_samples=10, temperature=0.1)
```

**Issue 4: LLM timeouts**
```
Solution:
1. Check internet connection
2. Verify API key is valid
3. Try different model: LLM_MODEL=openai/gpt-4-turbo
4. Add retry logic in llm_client.py
```

**Issue 5: Statistical tests failing**
```
Possible causes:
1. Too few data samples (need n > 20)
2. Variables have no variance
3. Missing values in data

Solution:
1. Increase sample size
2. Check data quality: data.describe()
3. Remove or impute missing values
```

### Getting Help

1. **Check Documentation**: README.md, ARCHITECTURE.md
2. **Run Tests**: `pytest tests/ -v`
3. **Enable Debugging**: Add print statements
4. **Check Examples**: Compare with working examples
5. **Create Issue**: Provide error message and code

### Best Practices

1. **Start Small**: Test with 3-5 variables first
2. **Describe Well**: Detailed variable descriptions help LLM
3. **Check Data**: Verify data quality before discovery
4. **Review Results**: Manually verify discovered relationships
5. **Iterate**: Refine descriptions based on results
6. **Save Work**: Always save reports and visualizations
7. **Track Costs**: Monitor API usage

---

## Next Steps

Now that you've completed the tutorial:

1. **Try the Examples**: Run the included example scripts
2. **Use Your Data**: Apply to your own domain
3. **Customize**: Modify prompts and tests for your needs
4. **Experiment**: Try different configurations
5. **Contribute**: Share improvements via pull requests

## Additional Resources

- **README.md**: Project overview
- **ARCHITECTURE.md**: System design details
- **QUICKSTART.md**: Quick reference guide
- **tests/**: Example code and patterns
- **examples/**: Working examples

Happy discovering! 🚀


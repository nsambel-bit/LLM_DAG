# Hybrid Causal Discovery System

A sophisticated causal discovery system that combines Large Language Model (LLM) knowledge extraction with statistical analysis to discover causal relationships from variable descriptions and optional observational data.

## Features

- **Hybrid Approach**: Combines LLM domain knowledge with statistical evidence
- **Uncertainty Quantification**: Tracks confidence scores for all causal relationships
- **Flexible**: Works with or without observational data
- **Conflict Resolution**: Intelligently resolves conflicts between knowledge-based and data-driven signals
- **Validation & Refinement**: Iterative validation and refinement of discovered graphs
- **Comprehensive Explanations**: Generates detailed explanations for causal relationships

## Architecture

The system consists of 6 main modules:

1. **Knowledge Extraction Engine**: Extracts causal knowledge from LLM with confidence scores
2. **Statistical Analysis Engine**: Computes statistical evidence from observational data
3. **Graph Constructor**: Builds causal graph using BFS with confidence tracking
4. **Conflict Resolver**: Resolves conflicts between LLM and statistical evidence
5. **Graph Validator**: Validates and refines discovered graphs
6. **Main Orchestrator**: Coordinates all modules

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nsambel-bit/LLM_DAG.git
cd LLM_DAG
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

```python
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig
from src.core.llm_client import get_llm_client
import pandas as pd

# Define variables
variables = [
    Variable(
        name='Smoking',
        description='Number of cigarettes smoked per day'
    ),
    Variable(
        name='Exercise',
        description='Hours of exercise per week'
    ),
    Variable(
        name='BMI',
        description='Body Mass Index'
    )
]

# Optional: Load observational data
data = pd.read_csv('your_data.csv')

# Initialize discovery system
discovery = HybridCausalDiscovery(
    llm_client=get_llm_client()
)

# Run discovery
result = discovery.discover(
    variables=variables,
    data=data  # Optional
)

# Access results
print(f"Discovered {len(result.graph.edges)} causal relationships")
result.graph.visualize('causal_graph.png')
```

## Examples

See the `examples/` directory for detailed examples:

- `basic_example.py`: Simple usage without data
- `health_example.py`: Healthcare domain with synthetic data
- `generate_sample_data.py`: Generate synthetic datasets for testing

## Running Tests

```bash
pytest tests/ -v --cov=src
```

## Configuration

Configure the system through environment variables (`.env`) or programmatically:

```python
config = DiscoveryConfig(
    resolve_conflicts=True,
    iterative_refinement=True,
    max_refinement_iterations=3,
    significance_level=0.05,
    confidence_threshold=0.5
)
```

## API Reference

### Variable
```python
Variable(name: str, description: str, metadata: Dict = {})
```

### HybridCausalDiscovery
```python
discovery = HybridCausalDiscovery(llm_client, config=None)
result = discovery.discover(variables, data=None, config=None)
```

### DiscoveryResult
```python
result.graph              # CausalGraph object
result.report             # Comprehensive report
result.validation         # Validation results
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Citation

If you use this system in your research, please cite:

```bibtex
@software{hybrid_causal_discovery,
  title={Hybrid Causal Discovery System},
  author={nsambel-bit},
  year={2024},
  url={https://github.com/nsambel-bit/LLM_DAG}
}
```


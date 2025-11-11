# Quick Start Guide

This guide will help you get started with the Hybrid Causal Discovery System in minutes.

## Prerequisites

- Python 3.8 or higher
- OpenRouter API key (for LLM access)

## Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp config/.env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_actual_api_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
```

**To get an OpenRouter API key:**
1. Visit https://openrouter.ai/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file

### 3. Verify Installation

Run a simple test:

```bash
python -c "from src.discovery import HybridCausalDiscovery; print('✓ Installation successful!')"
```

## Running Examples

### Example 1: Basic Discovery (Knowledge-Only)

Discover causal relationships using only LLM knowledge:

```bash
python examples/basic_example.py
```

This will:
- Use LLM to identify causal relationships
- Create a causal graph
- Generate explanations
- Save results to `outputs/` directory

### Example 2: Health Domain with Data

Discover causal relationships using both LLM knowledge and synthetic data:

```bash
python examples/health_example.py
```

This will:
- Generate synthetic health data (500 samples)
- Combine LLM knowledge with statistical analysis
- Resolve conflicts between knowledge and data
- Validate the discovered graph
- Save comprehensive results

### Example 3: Generate Custom Datasets

Generate synthetic datasets for testing:

```bash
python examples/generate_sample_data.py
```

This creates three datasets:
- `data/health_data.csv` - Health variables
- `data/economic_data.csv` - Economic variables
- `data/climate_data.csv` - Climate variables

## Using the System Programmatically

### Basic Usage (No Data)

```python
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable
from src.core.llm_client import get_llm_client

# Define variables
variables = [
    Variable(name="Smoking", description="Cigarettes per day"),
    Variable(name="Exercise", description="Hours of exercise per week"),
    Variable(name="BMI", description="Body Mass Index"),
]

# Initialize and run discovery
discovery = HybridCausalDiscovery(llm_client=get_llm_client())
result = discovery.discover(variables)

# Access results
print(f"Found {len(result.graph.edges)} causal relationships")
result.graph.visualize("my_graph.png")
```

### Advanced Usage (With Data)

```python
import pandas as pd
from src.discovery import HybridCausalDiscovery
from src.models.data_structures import Variable, DiscoveryConfig
from src.core.llm_client import get_llm_client

# Load your data
data = pd.read_csv("your_data.csv")

# Define variables
variables = [
    Variable(name="X", description="Description of X"),
    Variable(name="Y", description="Description of Y"),
    Variable(name="Z", description="Description of Z"),
]

# Configure discovery
config = DiscoveryConfig(
    resolve_conflicts=True,
    iterative_refinement=True,
    max_refinement_iterations=3,
    significance_level=0.05,
    n_samples=5
)

# Run discovery
discovery = HybridCausalDiscovery(llm_client=get_llm_client())
result = discovery.discover(variables, data=data, config=config)

# Analyze results
print("Root causes:", [r.name for r in result.graph.get_roots()])
print("Relationships:")
for edge in result.graph.edges:
    print(f"  {edge.source.name} → {edge.target.name} (conf={edge.confidence:.2f})")

# Save results
result.report.save("results.json")
result.graph.visualize("graph.png")
```

## Running Tests

Run the test suite to verify everything works:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_integration.py -v
```

## Output Files

After running examples, check the `outputs/` directory for:

- `*_graph.png` - Visual representation of causal graph
- `*_graph.json` - Machine-readable graph structure
- `*_report.json` - Comprehensive discovery report
- `*_explanation.txt` - Natural language explanation

## Troubleshooting

### Issue: "API key not provided" error

**Solution:** Ensure `.env` file exists with valid `OPENROUTER_API_KEY`

### Issue: Import errors

**Solution:** Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: No module named 'src'

**Solution:** Run scripts from the project root directory, not from subdirectories

### Issue: Statistical tests failing

**Solution:** Some statistical tests require minimum sample size. Ensure your data has at least 20-30 samples.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the architecture in the original design document
- Try with your own data and domain
- Customize the LLM prompts in `src/modules/knowledge_extractor.py`
- Adjust statistical tests in `src/modules/statistical_analyzer.py`

## Cost Considerations

Using OpenRouter API incurs costs based on:
- Model used (Claude 3.5 Sonnet is recommended)
- Number of tokens processed
- Number of API calls

For reference:
- Basic example (no data): ~5-10 API calls
- Health example (with data): ~10-20 API calls
- Each call: ~500-2000 tokens

Estimate: $0.10-$0.50 per complete discovery run

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review the code documentation
3. Create a new issue with details

## Tips for Best Results

1. **Write detailed variable descriptions** - The LLM relies heavily on these
2. **Use domain-appropriate language** - Medical terms for health, economic terms for finance, etc.
3. **Start small** - Test with 3-5 variables before scaling up
4. **Provide data when possible** - Hybrid approach works best
5. **Review rejected edges** - Often contain valuable insights
6. **Adjust n_samples** - Increase for more robust results (but higher cost)

Happy discovering! 🚀


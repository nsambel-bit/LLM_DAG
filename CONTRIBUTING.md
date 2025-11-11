# Contributing to Hybrid Causal Discovery System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. Check the existing issues to avoid duplicates
2. Verify you're using the latest version
3. Test with a minimal reproducible example

When submitting:
- Use a clear, descriptive title
- Provide steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version, dependencies)

### Suggesting Enhancements

We welcome feature requests! Please:
- Check if the feature has already been requested
- Explain the use case clearly
- Provide examples if possible
- Consider implementation complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/LLM_DAG.git
   cd LLM_DAG
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

3. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate
   - Update docstrings
   - Add tests for new features

4. **Run tests**
   ```bash
   pytest tests/ -v
   black src/ tests/ examples/  # Format code
   flake8 src/ tests/ examples/  # Check style
   mypy src/  # Type checking
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `perf:` Performance improvements

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a pull request on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints (Python 3.8+)
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public functions/classes

Example:
```python
def compute_confidence(
    source: Variable,
    target: Variable,
    samples: List[Sample]
) -> float:
    """
    Compute confidence score for a causal edge.
    
    Args:
        source: Source variable (cause)
        target: Target variable (effect)
        samples: List of LLM samples
        
    Returns:
        Confidence score in [0, 1]
    """
    # Implementation
    pass
```

### Testing

- Write unit tests for new functions
- Aim for >80% code coverage
- Use pytest fixtures for common setups
- Mock LLM calls in tests

Example:
```python
def test_knowledge_extractor():
    """Test knowledge extractor with mock LLM."""
    mock_llm = Mock()
    mock_llm.complete.return_value = "..."
    
    extractor = KnowledgeExtractor(mock_llm)
    result = extractor.identify_root_causes(variables)
    
    assert len(result) > 0
```

### Documentation

- Update README.md if adding major features
- Add docstrings to new functions/classes
- Update ARCHITECTURE.md for architectural changes
- Add examples for new functionality

## Areas for Contribution

### High Priority
1. **Performance optimization**
   - Parallel LLM calls
   - Caching improvements
   - Memory efficiency

2. **Statistical methods**
   - Additional independence tests
   - Bootstrapping for confidence intervals
   - FCI algorithm for latent variables

3. **LLM prompting**
   - Improved prompt engineering
   - Few-shot examples
   - Chain-of-thought reasoning

### Medium Priority
1. **Validation tests**
   - Additional consistency checks
   - Cross-validation approaches
   - Sensitivity analysis

2. **Visualization**
   - Interactive graph exploration
   - Confidence heatmaps
   - Mechanism diagrams

3. **Documentation**
   - More examples
   - Video tutorials
   - API documentation

### Low Priority
1. **Alternative LLM providers**
   - Local models (Llama, Mistral)
   - Other APIs (Anthropic direct, OpenAI)

2. **Export formats**
   - GraphML, GEXF
   - R integration
   - Neo4j export

## Testing Your Changes

### Run Full Test Suite
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Test Examples
```bash
python test_setup.py
python examples/basic_example.py
python examples/health_example.py
```

### Check Code Quality
```bash
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```

## Release Process

1. Update version in `setup.py` and `src/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
5. Push tag: `git push origin v0.2.0`
6. Create GitHub release with notes

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉


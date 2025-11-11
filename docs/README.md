# Documentation

This directory contains comprehensive documentation for the Hybrid Causal Discovery System.

## Scientific Paper

**SCIENTIFIC_PAPER.tex** - Complete scientific paper (LaTeX source)

This document provides:
- Formal mathematical framework
- Algorithm descriptions with pseudocode
- Implementation details
- Experimental results
- Performance analysis

### Compiling to PDF

#### Option 1: Local Compilation (requires LaTeX)

```bash
cd docs
python compile_paper.py
```

Requirements:
- **Linux**: `sudo apt-get install texlive-latex-extra`
- **macOS**: `brew install mactex`
- **Windows**: Download and install [MiKTeX](https://miktex.org/)

#### Option 2: Online Compilation (no installation needed)

1. Go to [Overleaf.com](https://www.overleaf.com/)
2. Create a new blank project
3. Upload `SCIENTIFIC_PAPER.tex`
4. Click "Recompile" to generate PDF
5. Download the PDF

## Key Sections in the Paper

### 1. Introduction
- Motivation for hybrid approach
- Comparison with traditional methods
- Main contributions

### 2. Mathematical Framework
- Problem formulation
- Self-consistency sampling for uncertainty
- Statistical evidence measures
- Confidence fusion formula
- Graph construction algorithm

### 3. Implementation
- System architecture (6 modules)
- Data structures
- Complexity analysis
- Code organization

### 4. Experimental Results
- Health domain case study
- Performance metrics (Precision: 100%, Recall: 100%)
- Ablation study comparing hybrid vs. pure approaches
- Scalability analysis

### 5. Discussion
- Strengths and limitations
- Future research directions
- Practical applications

## Additional Documentation

- **../README.md** - Project overview and quick start
- **../QUICKSTART.md** - Step-by-step setup guide
- **../ARCHITECTURE.md** - Detailed system architecture
- **../TUTORIAL.md** - Comprehensive tutorials
- **../PROJECT_SUMMARY.md** - Complete project summary

## Citation

If you use this system in your research, please cite:

```bibtex
@article{llmdag2024,
  title={Hybrid Causal Discovery: Combining Large Language Models with Statistical Analysis},
  author={LLM\_DAG System},
  year={2024},
  note={Available at: https://github.com/yourusername/LLM_DAG}
}
```

## Contact

For questions or issues:
- Open an issue on GitHub
- Check the documentation first
- Review example outputs in `outputs/` directory


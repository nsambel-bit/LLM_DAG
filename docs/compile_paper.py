"""Compile LaTeX scientific paper to PDF."""

import subprocess
import sys
import os

def compile_latex_to_pdf():
    """Compile the scientific paper from LaTeX to PDF."""
    
    latex_file = "SCIENTIFIC_PAPER.tex"
    
    if not os.path.exists(latex_file):
        print(f"Error: {latex_file} not found")
        return False
    
    print("Compiling LaTeX to PDF...")
    print("Note: This requires pdflatex to be installed")
    print("Install via: sudo apt-get install texlive-latex-extra (Linux)")
    print("           or brew install mactex (macOS)")
    print("           or download MikTeX (Windows)")
    
    try:
        # Run pdflatex twice for references
        for i in range(2):
            print(f"\nPass {i+1}/2...")
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", latex_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("LaTeX compilation failed:")
                print(result.stdout)
                print(result.stderr)
                return False
        
        # Clean up auxiliary files
        extensions = ['.aux', '.log', '.out', '.toc']
        for ext in extensions:
            aux_file = latex_file.replace('.tex', ext)
            if os.path.exists(aux_file):
                os.remove(aux_file)
        
        pdf_file = latex_file.replace('.tex', '.pdf')
        print(f"\n✓ Successfully generated {pdf_file}")
        return True
        
    except FileNotFoundError:
        print("\nError: pdflatex not found. Please install LaTeX distribution.")
        print("\nAlternatively, you can:")
        print("1. Copy SCIENTIFIC_PAPER.tex to Overleaf.com")
        print("2. Compile online and download PDF")
        return False
    except Exception as e:
        print(f"\nError during compilation: {e}")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = compile_latex_to_pdf()
    sys.exit(0 if success else 1)


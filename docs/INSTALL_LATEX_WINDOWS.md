# Installing LaTeX on Windows

## Quick Install (Recommended)

### Option A: MiKTeX (Smaller, ~200 MB)

1. Download: https://miktex.org/download
2. Run the installer
3. Choose "Install missing packages on-the-fly: Yes"
4. Complete installation

### Option B: TeX Live (Full, ~4 GB)

1. Download: https://tug.org/texlive/windows.html
2. Run `install-tl-windows.exe`
3. Wait for full installation (takes 30-60 minutes)

## After Installation

### Verify Installation

```cmd
where pdflatex
```

Should show the path to pdflatex.exe

### Compile Your Paper

```cmd
cd C:\Users\nsamb\Downloads\LLM_DAG\docs
python compile_paper.py
```

This will create `SCIENTIFIC_PAPER.pdf` in the `docs/` folder!

## Troubleshooting

### "pdflatex not found" after installation
- Close and reopen your terminal/PowerShell
- Or restart your computer
- Add to PATH manually: Control Panel → System → Environment Variables

### "Missing package" errors with MiKTeX
- MiKTeX will prompt to install missing packages
- Click "Yes" to install them automatically
- Or use: `mpm --install=<package-name>`

### Compilation errors
- Check the .log file for details
- Common issues:
  - Missing packages (MiKTeX installs automatically)
  - Invalid LaTeX syntax (check SCIENTIFIC_PAPER.tex)

## Alternative: Compile Manually

If the Python script doesn't work:

```cmd
cd C:\Users\nsamb\Downloads\LLM_DAG\docs
pdflatex -interaction=nonstopmode SCIENTIFIC_PAPER.tex
pdflatex -interaction=nonstopmode SCIENTIFIC_PAPER.tex
```

Run twice to resolve cross-references.


@echo off
REM Windows batch script to compile LaTeX paper to PDF

echo ========================================
echo Compiling Scientific Paper to PDF
echo ========================================
echo.

REM Check if pdflatex is installed
where pdflatex >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pdflatex is not installed
    echo.
    echo Please install LaTeX first:
    echo   Option 1: MiKTeX - https://miktex.org/download
    echo   Option 2: TeX Live - https://tug.org/texlive/
    echo.
    echo Or use Overleaf online: https://www.overleaf.com
    echo.
    pause
    exit /b 1
)

echo Found pdflatex!
echo.

REM Navigate to docs directory
cd /d "%~dp0"

REM Check if SCIENTIFIC_PAPER.tex exists
if not exist "SCIENTIFIC_PAPER.tex" (
    echo [ERROR] SCIENTIFIC_PAPER.tex not found
    pause
    exit /b 1
)

echo Compiling LaTeX document...
echo.

echo [Pass 1/2] First compilation...
pdflatex -interaction=nonstopmode SCIENTIFIC_PAPER.tex
if errorlevel 1 (
    echo [ERROR] First pass failed
    echo Check SCIENTIFIC_PAPER.log for details
    pause
    exit /b 1
)

echo.
echo [Pass 2/2] Second compilation (for cross-references)...
pdflatex -interaction=nonstopmode SCIENTIFIC_PAPER.tex
if errorlevel 1 (
    echo [ERROR] Second pass failed
    echo Check SCIENTIFIC_PAPER.log for details
    pause
    exit /b 1
)

echo.
echo Cleaning up auxiliary files...
del SCIENTIFIC_PAPER.aux 2>nul
del SCIENTIFIC_PAPER.log 2>nul
del SCIENTIFIC_PAPER.out 2>nul
del SCIENTIFIC_PAPER.toc 2>nul

echo.
echo ========================================
echo SUCCESS! PDF Generated
echo ========================================
echo.
echo Output: SCIENTIFIC_PAPER.pdf
echo Location: %cd%\SCIENTIFIC_PAPER.pdf
echo.
echo Opening PDF...
start SCIENTIFIC_PAPER.pdf

pause


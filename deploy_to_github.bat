@echo off
REM Deployment script for Windows
REM Deploy Hybrid Causal Discovery System to GitHub

echo ========================================
echo Deploying to GitHub
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo [1/5] Initializing Git repository...
git init
if errorlevel 1 (
    echo [ERROR] Failed to initialize Git repository
    pause
    exit /b 1
)

echo [2/5] Adding all files...
git add .
if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)

echo [3/5] Creating initial commit...
git commit -m "Initial commit: Hybrid Causal Discovery System v0.1.0"
if errorlevel 1 (
    echo [ERROR] Failed to create commit
    pause
    exit /b 1
)

echo [4/5] Adding remote repository...
git remote add origin https://github.com/nsambel-bit/LLM_DAG.git
if errorlevel 1 (
    echo [WARN] Remote might already exist, continuing...
)

echo [5/5] Setting main branch...
git branch -M main

echo.
echo ========================================
echo Ready to push to GitHub!
echo ========================================
echo.
echo Next step: Create the repository on GitHub
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: LLM_DAG
echo 3. Description: Hybrid causal discovery combining LLM with statistical analysis
echo 4. Visibility: Public
echo 5. Do NOT initialize with README
echo 6. Click "Create repository"
echo.
echo Then run: git push -u origin main
echo.
echo Or run this command now to push:
echo    git push -u origin main
echo.
pause

REM Optionally push now
set /p PUSH="Push to GitHub now? (y/n): "
if /i "%PUSH%"=="y" (
    echo.
    echo Pushing to GitHub...
    git push -u origin main
    if errorlevel 1 (
        echo [ERROR] Failed to push to GitHub
        echo Make sure you have created the repository on GitHub first
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo SUCCESS! Deployed to GitHub
    echo ========================================
    echo.
    echo View at: https://github.com/nsambel-bit/LLM_DAG
    echo.
)

pause


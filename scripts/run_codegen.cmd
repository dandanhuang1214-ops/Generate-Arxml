@echo off
setlocal
cd /d "%~dp0.."
set "PYTHONPATH=src"

set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

"%PYTHON%" -c "import arxml_codegen, lxml, openpyxl, yaml" >nul 2>nul
if errorlevel 1 (
  echo Python environment is unavailable or incomplete.
  echo Run: .venv\Scripts\python.exe -m pip install -e ".[dev]"
  exit /b 1
)

"%PYTHON%" -m arxml_codegen.cli %*
exit /b %errorlevel%

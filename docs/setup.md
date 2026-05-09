# Setup

## Python version

Recommended:

- Python `3.10` or `3.11`

## Virtual environment

Create the environment in the project root:

```powershell
cd D:\work\SOA\code
py -3.11 -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

## Install dependencies

Editable install:

```powershell
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Verify installation

```powershell
python -m arxml_codegen.cli --help
pytest
```

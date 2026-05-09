# Usage

## Goal

Use one standard Excel workbook as the source of truth and generate one importable `ARXML`.

## Recommended workflow

1. Open the project in VS Code.
2. Activate the virtual environment.
3. Fill the Excel workbook.
4. Update `config/project.yaml` if workbook or output paths change.
5. Run a dry run.
6. Run the real generation.
7. Import the generated `ARXML` into DaVinci Developer.

## Step-by-step

### 1. Go to the project root

```powershell
cd D:\work\SOA\code
```

### 2. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Check the workbook path

Default config:

- workbook: `../输入.xlsx`
- output: `output/generated_from_excel.arxml`

Edit [project.yaml](../config/project.yaml) if needed.

### 4. Run a dry run

```powershell
python -m arxml_codegen.cli --config config/project.yaml --dry-run
```

This checks:

- workbook loading
- sheet parsing
- row counts

### 5. Generate ARXML

```powershell
python -m arxml_codegen.cli --config config/project.yaml
```

### 6. Import output

Import:

- [generated_from_excel.arxml](../output/generated_from_excel.arxml)

into DaVinci Developer.

## Workbook meaning

- `Components`
  Defines component-level objects.
- `Ports`
  Defines both `SR` and `CS` ports.
- `Arguments`
  Defines `CS` operation parameters.
- `ValueMap`
  Defines enum text/value mappings.
- `Runnables`
  Defines `Init`, `Period`, and `Invocation` runnables.

## Typical supporting scripts

- Create or refresh the Excel template:

```powershell
.\scripts\create_excel_template.ps1
```

- Backfill workbook content from an existing `ARXML`:

```powershell
.\scripts\fill_input_from_arxml.ps1
```

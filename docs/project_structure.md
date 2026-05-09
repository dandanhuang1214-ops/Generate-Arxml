# Project Structure

## Goal

This project is intended to replace repetitive DaVinci Developer modeling work with a reusable workbook-driven generation flow.

## Main chain

Input:

- unified Excel workbook

Process:

- Python reader
- Python normalization
- Python `ARXML` generation

Output:

- generated `ARXML`

## Directory responsibilities

### `src/arxml_codegen/`

Core Python package.

### `src/arxml_codegen/cli.py`

Project entry point.

Responsibilities:

- load config
- load workbook
- trigger generation
- print summary

### `src/arxml_codegen/excel/reader.py`

Workbook parser.

Responsibilities:

- read `Components`
- read `Ports`
- read `Arguments`
- read `ValueMap`
- read `Runnables`

### `src/arxml_codegen/models/schema.py`

Shared in-memory model.

Responsibilities:

- define row structures
- define workbook aggregate structure

### `src/arxml_codegen/generator/arxml_writer.py`

ARXML builder.

Responsibilities:

- build AUTOSAR root and packages
- generate data types
- generate `SR` interfaces
- generate `CS` interfaces and operations
- generate SWCs, ports, runnables, and events

### `config/project.yaml`

Central project configuration.

Responsibilities:

- workbook location
- output location
- optional template reference

### `scripts/`

Convenience scripts.

- `run_codegen.ps1`
  Main generation entry.
- `create_excel_template.ps1`
  Rebuild standard workbook template.
- `fill_input_from_arxml.ps1`
  Reverse-fill workbook content from an existing `ARXML`.

### `data/input/`

Workbook inputs.

### `output/`

Generated `ARXML` outputs.

### `docs/`

Usage, setup, template definition, and project notes.

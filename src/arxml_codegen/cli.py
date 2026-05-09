from __future__ import annotations

import argparse
from pathlib import Path

from arxml_codegen.excel.reader import load_workbook_model
from arxml_codegen.excel.template import create_template
from arxml_codegen.generator.arxml_writer import load_config, validate_model, write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arxml-codegen",
        description="Generate AUTOSAR Classic SWC/Composition ARXML from Excel definitions.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/project.yaml"),
        help="Path to the project YAML configuration file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print the execution plan without writing ARXML.",
    )
    parser.add_argument(
        "--create-template",
        type=Path,
        help="Create a standard Excel input template at the given path and exit.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.create_template:
        create_template(args.create_template)
        print(f"Template created: {args.create_template}")
        return 0

    config = load_config(args.config)
    model = load_workbook_model(config.workbook)
    validation = validate_model(model)

    print(f"Config: {args.config}")
    print(f"Workbook: {config.workbook}")
    print(f"Output ARXML: {config.output}")
    print(f"Report: {config.report}")
    if config.matlab_init:
        print(f"MATLAB init: {config.matlab_init}")
    print(
        "Loaded "
        f"{len(model.components)} components, "
        f"{len(model.data_types)} data types, "
        f"{len(model.port_interfaces)} interfaces, "
        f"{len(model.operations)} operation arguments, "
        f"{len(model.ports)} ports, "
        f"{len(model.runnables)} runnables, "
        f"{len(model.runnable_events)} events, "
        f"{len(model.composition_connectors)} connectors."
    )

    if validation.errors:
        print("Validation errors:")
        for error in validation.errors:
            print(f"  - {error}")
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings[:20]:
            print(f"  - {warning}")
        if len(validation.warnings) > 20:
            print(f"  ... {len(validation.warnings) - 20} more warnings")

    if args.dry_run:
        print("Dry run enabled. No files written.")
        return 1 if validation.errors else 0

    write_outputs(model, config)
    print("ARXML generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from arxml_codegen.excel.reader import load_workbook_v2
from arxml_codegen.excel.template import create_template_v2
from arxml_codegen.generator.arxml_writer import (
    GeneratorConfig,
    load_config,
    summarize_v2,
    validate_model_v2,
    write_outputs,
)
from arxml_codegen.validator.engine import RULES, run_all as run_core_validation, summarize


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
        create_template_v2(args.create_template)
        print(f"Template created: {args.create_template}")
        return 0

    config: GeneratorConfig = load_config(args.config)
    model = load_workbook_v2(config.workbook)
    errors = validate_model_v2(model)

    print(f"Config: {args.config}")
    print(f"Workbook: {config.workbook}")
    print(f"Output ARXML: {config.output}")
    print(f"Report: {config.report}")
    if config.matlab_init:
        print(f"MATLAB init: {config.matlab_init}")
    print(summarize_v2(model))

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")

    print(f"\nCORE Validation ({len(RULES)} rule groups):")
    core_findings = run_core_validation(model)
    core_errors = [f for f in core_findings if f.severity.value == "ERROR"]
    summary = summarize(core_findings)
    sev = summary["by_severity"]
    grp = summary["by_group"]
    print(f"  Result: {sev['ERROR']} errors, {sev['WARNING']} warnings, {sev['INFO']} info")
    if grp:
        for g, count in sorted(grp.items()):
            print(f"    {g}: {count} finding(s)")
    if core_findings:
        if any(f.severity.value == "ERROR" for f in core_findings):
            print("\n  Errors:")
            for f in core_findings:
                if f.severity.value == "ERROR":
                    print(f"    {f}")
        if any(f.severity.value == "WARNING" for f in core_findings):
            print("\n  Warnings:")
            for f in core_findings:
                if f.severity.value == "WARNING":
                    print(f"    {f}")
    else:
        print("  All CORE rules passed. No findings.")

    if args.dry_run:
        print("Dry run enabled. No files written.")
        return 1 if errors or core_errors else 0
    if errors or core_errors:
        print("ARXML generation skipped because model or CORE validation failed.")
        return 1

    write_outputs(model, config, errors, core_findings)
    print("ARXML generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

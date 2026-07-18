from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from arxml_codegen.contract.docx_loader import extract_contract_from_docx
from arxml_codegen.contract.embedded_excel_loader import extract_signal_atomic_contract_from_docx
from arxml_codegen.contract.excel_builder import write_contract_excel
from arxml_codegen.contract.gap_report import build_gap_report, gap_report_markdown
from arxml_codegen.contract.schema import DeliveryContract
from arxml_codegen.excel.reader import load_workbook_v2
from arxml_codegen.generator.arxml_writer import (
    GeneratorConfig,
    validate_model_v2,
    write_outputs,
)
from arxml_codegen.validator.engine import run_all as run_core_validation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert ARXML delivery DOCX documents to canonical contract JSON and Excel drafts."
    )
    parser.add_argument("--input", type=Path, help="Input DOCX path.")
    parser.add_argument("--contract", type=Path, help="Input or output canonical contract JSON path.")
    parser.add_argument("--excel", type=Path, help="Optional output Excel v2 workbook path.")
    parser.add_argument(
        "--issues",
        type=Path,
        help="Optional output gap report Markdown path. Kept for backward compatibility.",
    )
    parser.add_argument("--report-json", type=Path, help="Optional output gap report JSON path.")
    parser.add_argument("--arxml", type=Path, help="Optional final ARXML output path.")
    parser.add_argument(
        "--generation-report",
        type=Path,
        help="Optional generation report path used with --arxml.",
    )
    parser.add_argument("--mode", choices=["signal", "soa", "mixed"], default="signal")
    parser.add_argument(
        "--profile",
        choices=["generic", "signal_atomic_davinci", "mixed_signal_soa"],
        default=None,
        help=(
            "Generation profile. signal_atomic_davinci is the single Atomic SWC signal style; "
            "mixed_signal_soa adds multi-SWC C/S, Composition and connectors while preserving "
            "the same DaVinci S/R and data-type rules."
        ),
    )
    args = parser.parse_args()

    if args.input:
        requested_profile = args.profile or ""
        if requested_profile == "signal_atomic_davinci":
            contract = extract_contract_from_docx(args.input, mode=args.mode)
            if not contract.signals:
                contract = extract_signal_atomic_contract_from_docx(args.input)
        else:
            contract = extract_contract_from_docx(args.input, mode=args.mode)
        if requested_profile:
            contract.project.generation_profile = requested_profile
        contract.metadata["generation_profile"] = contract.project.generation_profile
        if args.contract:
            args.contract.parent.mkdir(parents=True, exist_ok=True)
            args.contract.write_text(
                json.dumps(contract.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    elif args.contract:
        contract = DeliveryContract.from_dict(json.loads(args.contract.read_text(encoding="utf-8")))
    else:
        parser.error("Provide --input DOCX or --contract JSON.")

    model = None
    validation_errors: list[str] = []
    core_findings = []
    if args.excel:
        write_contract_excel(contract, args.excel)
        model = load_workbook_v2(args.excel)
        validation_errors = validate_model_v2(model)
        core_findings = run_core_validation(model)

    if args.issues or args.report_json:
        if model is None:
            parser.error("--issues/--report-json require --excel so the generated workbook can be validated.")
        report = build_gap_report(contract, model, validation_errors, core_findings)

    if args.issues:
        args.issues.parent.mkdir(parents=True, exist_ok=True)
        args.issues.write_text(gap_report_markdown(report), encoding="utf-8")
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    has_open_issues = any(issue.status.lower() == "open" for issue in contract.open_issues)
    has_core_errors = any(finding.severity.value == "ERROR" for finding in core_findings)
    blocked = bool(has_open_issues or validation_errors or has_core_errors)
    if args.arxml:
        if model is None or args.excel is None:
            parser.error("--arxml requires --excel so the validated workbook is the generation input.")
        if blocked:
            print("ARXML generation skipped because the contract or model has unresolved errors.")
        else:
            generation_report = args.generation_report or args.arxml.with_name(
                args.arxml.stem + "_generation_report.md"
            )
            config = GeneratorConfig(
                workbook=args.excel,
                output=args.arxml,
                report=generation_report,
                matlab_init=None,
                autosar_version=contract.project.target_autosar_version or "4-3-0",
            )
            write_outputs(model, config, validation_errors, core_findings)

    print(
        "Contract pipeline completed: "
        f"{len(contract.swcs)} SWCs, "
        f"{len(contract.signals)} signals, "
        f"{len(contract.services)} services, "
        f"{len(contract.open_issues)} open issues, "
        f"{len(validation_errors)} model validation errors, "
        f"{sum(1 for finding in core_findings if finding.severity.value == 'ERROR')} CORE errors."
    )
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())

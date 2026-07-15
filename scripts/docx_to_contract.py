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
from arxml_codegen.generator.arxml_writer import validate_model_v2
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
    parser.add_argument("--mode", choices=["signal", "soa", "mixed"], default="signal")
    parser.add_argument(
        "--profile",
        choices=["generic", "signal_atomic_davinci"],
        default="generic",
        help="Generation profile. signal_atomic_davinci matches the single Atomic SWC signal style used by DaVinci examples.",
    )
    args = parser.parse_args()

    if args.input:
        if args.profile == "signal_atomic_davinci":
            contract = extract_contract_from_docx(args.input, mode=args.mode)
            if not contract.signals:
                contract = extract_signal_atomic_contract_from_docx(args.input)
        else:
            contract = extract_contract_from_docx(args.input, mode=args.mode)
        contract.project.generation_profile = args.profile
        contract.metadata["generation_profile"] = args.profile
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

    print(
        "Contract pipeline completed: "
        f"{len(contract.swcs)} SWCs, "
        f"{len(contract.signals)} signals, "
        f"{len(contract.services)} services, "
        f"{len(contract.open_issues)} open issues, "
        f"{len(validation_errors)} model validation errors, "
        f"{sum(1 for finding in core_findings if finding.severity.value == 'ERROR')} CORE errors."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

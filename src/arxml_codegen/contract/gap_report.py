from __future__ import annotations

from dataclasses import asdict, dataclass

from arxml_codegen.contract.schema import DeliveryContract
from arxml_codegen.models.schema import WorkbookV2Model
from arxml_codegen.validator.engine import summarize
from arxml_codegen.validator.finding import Finding


@dataclass(slots=True)
class GapItem:
    kind: str
    severity: str
    code: str
    field: str
    message: str
    location: str = ""
    suggestion: str = ""
    source: str = ""
    owner: str = ""
    status: str = "open"


@dataclass(slots=True)
class GapReport:
    source_docx: str
    mode: str
    counts: dict[str, int]
    validation_errors: list[str]
    core_summary: dict[str, object]
    items: list[GapItem]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_docx": self.source_docx,
            "mode": self.mode,
            "counts": self.counts,
            "validation_errors": self.validation_errors,
            "core_summary": self.core_summary,
            "items": [asdict(item) for item in self.items],
        }


def build_gap_report(
    contract: DeliveryContract,
    model: WorkbookV2Model,
    validation_errors: list[str],
    core_findings: list[Finding],
) -> GapReport:
    items: list[GapItem] = []

    for issue in contract.open_issues:
        items.append(
            GapItem(
                kind="open_issue",
                severity="QUESTION",
                code="CONTRACT-OPEN-ISSUE",
                field=issue.field,
                message=issue.question,
                suggestion=issue.suggested_default,
                source=issue.source,
                owner=issue.owner,
                status=issue.status,
            )
        )

    for error in validation_errors:
        items.append(
            GapItem(
                kind="model_validation",
                severity="ERROR",
                code="MODEL-VALIDATION",
                field="",
                message=error,
                status="open",
            )
        )

    for finding in core_findings:
        items.append(
            GapItem(
                kind="core_rule",
                severity=finding.severity.value,
                code=finding.code,
                field="",
                message=finding.message,
                location=finding.location,
                suggestion=finding.suggestion,
                status="open",
            )
        )

    return GapReport(
        source_docx=contract.metadata.get("source_docx", ""),
        mode=contract.metadata.get("mode", ""),
        counts={
            "swcs": len(contract.swcs),
            "signals": len(contract.signals),
            "services": len(contract.services),
            "operation_args": len(contract.operation_args),
            "record_elements": len(contract.record_elements),
            "runnables": len(contract.runnables),
            "components": len(model.components),
            "ports": len(model.ports),
            "connectors": len(model.composition_connectors),
            "runnable_events": len(model.runnable_events),
            "runnable_accesses": len(model.runnable_accesses),
            "open_issues": len(contract.open_issues),
            "validation_errors": len(validation_errors),
            "core_findings": len(core_findings),
        },
        validation_errors=validation_errors,
        core_summary=summarize(core_findings),
        items=items,
    )


def gap_report_markdown(report: GapReport) -> str:
    lines = [
        "# ARXML Delivery Gap Report",
        "",
        f"- Source: `{report.source_docx}`",
        f"- Mode: `{report.mode}`",
        f"- Open issues: {report.counts['open_issues']}",
        f"- Model validation errors: {report.counts['validation_errors']}",
        f"- CORE findings: {report.counts['core_findings']}",
        "",
        "## Extracted Scope",
        "",
        "| Item | Count |",
        "|---|---:|",
    ]
    for key in [
        "swcs",
        "signals",
        "services",
        "operation_args",
        "record_elements",
        "runnables",
        "components",
        "ports",
        "connectors",
        "runnable_events",
        "runnable_accesses",
    ]:
        lines.append(f"| {key} | {report.counts[key]} |")

    lines.extend(
        [
            "",
            "## CORE Summary",
            "",
            "| Severity | Count |",
            "|---|---:|",
        ]
    )
    by_severity = report.core_summary.get("by_severity", {})
    for severity in ["ERROR", "WARNING", "INFO"]:
        lines.append(f"| {severity} | {by_severity.get(severity, 0)} |")

    lines.extend(["", "## Gap Items", ""])
    if not report.items:
        lines.append("- none")
    else:
        lines.append("| Kind | Severity | Code | Field/Location | Message | Suggestion |")
        lines.append("|---|---|---|---|---|---|")
        for item in report.items:
            field_or_location = item.field or item.location
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md(item.kind),
                        _md(item.severity),
                        _md(item.code),
                        _md(field_or_location),
                        _md(item.message),
                        _md(item.suggestion),
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Suggested Workflow",
            "",
            "1. Resolve all `ERROR` items before importing generated ARXML into DaVinci Developer.",
            "2. Review `QUESTION` items with the upstream owner and update the delivery document or contract JSON.",
            "3. Treat `WARNING` items as modeling risks; either fix them or record why they are acceptable.",
        ]
    )
    return "\n".join(lines) + "\n"


def _md(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", "<br>")

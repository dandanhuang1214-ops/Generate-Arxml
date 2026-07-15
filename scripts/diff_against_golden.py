from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from lxml import etree


NS = {"ar": "http://autosar.org/schema/r4.0"}
INTERESTING_TAGS = {
    "APPLICATION-VALUE-SPECIFICATION",
    "NUMERICAL-VALUE-SPECIFICATION",
    "RECORD-VALUE-SPECIFICATION",
    "TEXT-VALUE-SPECIFICATION",
    "COMPU-METHOD",
    "DATA-CONSTR",
    "NONQUEUED-RECEIVER-COM-SPEC",
    "NONQUEUED-SENDER-COM-SPEC",
    "QUEUED-RECEIVER-COM-SPEC",
    "QUEUED-SENDER-COM-SPEC",
    "CLIENT-COM-SPEC",
    "SERVER-COM-SPEC",
}


@dataclass(slots=True)
class IndexedElement:
    path: str
    tag: str
    summary: dict[str, object] = field(default_factory=dict)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare generated ARXML with a DaVinci Developer golden ARXML by semantic structure."
    )
    parser.add_argument("--generated", required=True, type=Path, help="Generated ARXML to inspect.")
    parser.add_argument("--golden", required=True, type=Path, help="DaVinci Developer exported ARXML.")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/golden_diff_report.md"),
        help="Markdown report path.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Optional JSON report path for tooling.",
    )
    args = parser.parse_args()

    generated = index_arxml(args.generated)
    golden = index_arxml(args.golden)
    report = build_report(generated, golden, args.generated, args.golden)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(diff_payload(generated, golden), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    print(f"Golden diff report written: {args.report}")
    return 0


def index_arxml(path: Path) -> dict[str, IndexedElement]:
    tree = etree.parse(str(path))
    root = tree.getroot()
    indexed: dict[str, IndexedElement] = {}
    for element in root.iter():
        tag = local_name(element)
        if tag not in INTERESTING_TAGS:
            continue
        semantic_path = short_name_path(element)
        if not semantic_path:
            continue
        indexed[semantic_path] = IndexedElement(
            path=semantic_path,
            tag=tag,
            summary=summarize_element(element),
        )
    return indexed


def build_report(
    generated: dict[str, IndexedElement],
    golden: dict[str, IndexedElement],
    generated_path: Path,
    golden_path: Path,
) -> str:
    payload = diff_payload(generated, golden)
    type_counts = Counter(item.tag for item in generated.values())
    golden_type_counts = Counter(item.tag for item in golden.values())
    category_counts = Counter(item["category"] for item in payload["action_items"])
    lines = [
        "# Golden ARXML Diff Report",
        "",
        "This report compares semantic ARXML structures by SHORT-NAME path.",
        "It intentionally ignores UUIDs, timestamps, whitespace, and raw element order.",
        "",
        "## Inputs",
        "",
        f"- Generated: `{generated_path}`",
        f"- Golden: `{golden_path}`",
        "",
        "## Indexed Elements",
        "",
        f"- Generated indexed elements: {len(generated)}",
        f"- Golden indexed elements: {len(golden)}",
        "",
        "### Generated Type Counts",
        "",
        *_counter_lines(type_counts),
        "",
        "### Golden Type Counts",
        "",
        *_counter_lines(golden_type_counts),
        "",
        "## Differences",
        "",
        f"- Missing in generated: {len(payload['missing_in_generated'])}",
        f"- Extra in generated: {len(payload['extra_in_generated'])}",
        f"- Summary mismatches: {len(payload['summary_mismatches'])}",
        "",
        "## Action Categories",
        "",
        *_counter_lines(category_counts),
        "",
    ]
    lines.extend(_action_section(payload["action_items"]))
    lines.extend(_section("Missing In Generated", payload["missing_in_generated"]))
    lines.extend(_section("Extra In Generated", payload["extra_in_generated"]))
    lines.extend(_mismatch_section(payload["summary_mismatches"]))
    return "\n".join(lines) + "\n"


def diff_payload(
    generated: dict[str, IndexedElement],
    golden: dict[str, IndexedElement],
) -> dict[str, object]:
    generated_keys = set(generated)
    golden_keys = set(golden)
    common = sorted(generated_keys & golden_keys)
    mismatches = []
    for key in common:
        if generated[key].tag != golden[key].tag or generated[key].summary != golden[key].summary:
            mismatches.append(
                {
                    "path": key,
                    "generated_tag": generated[key].tag,
                    "golden_tag": golden[key].tag,
                    "generated": generated[key].summary,
                    "golden": golden[key].summary,
                }
            )
    action_items = build_action_items(
        missing=sorted(golden_keys - generated_keys),
        extra=sorted(generated_keys - golden_keys),
        mismatches=mismatches,
    )
    return {
        "missing_in_generated": sorted(golden_keys - generated_keys),
        "extra_in_generated": sorted(generated_keys - golden_keys),
        "summary_mismatches": mismatches,
        "action_items": action_items,
    }


def build_action_items(
    *,
    missing: list[str],
    extra: list[str],
    mismatches: list[dict[str, object]],
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for path in missing:
        category = classify_path(path)
        _append_action(
            items,
            seen,
            category,
            "missing_in_generated",
            path,
            suggestion_for(category, "missing_in_generated"),
        )
    for path in extra:
        category = classify_path(path)
        _append_action(
            items,
            seen,
            category,
            "extra_in_generated",
            path,
            suggestion_for(category, "extra_in_generated"),
        )
    for mismatch in mismatches:
        path = str(mismatch["path"])
        category = classify_path(path, mismatch)
        _append_action(
            items,
            seen,
            category,
            "summary_mismatch",
            path,
            suggestion_for(category, "summary_mismatch"),
        )
    severity_order = {"init_value": 0, "record_init_value": 1, "com_spec": 2, "compu_method": 3, "data_constr": 4}
    return sorted(items, key=lambda item: (severity_order.get(item["category"], 99), item["category"], item["path"]))


def _append_action(
    items: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    category: str,
    diff_type: str,
    path: str,
    suggestion: str,
) -> None:
    key = (category, diff_type, path)
    if key in seen:
        return
    seen.add(key)
    items.append(
        {
            "category": category,
            "diff_type": diff_type,
            "path": path,
            "suggestion": suggestion,
        }
    )


def classify_path(path: str, mismatch: dict[str, object] | None = None) -> str:
    text = path.upper()
    if "RECORD-VALUE-SPECIFICATION" in text:
        return "record_init_value"
    if "INIT-VALUE" in text or "VALUE-SPECIFICATION" in text:
        return "init_value"
    if "COM-SPEC" in text:
        return "com_spec"
    if "COMPU-METHOD" in text or "/COMPUMETHODS/" in text:
        return "compu_method"
    if "DATA-CONSTR" in text or "/DATACONSTRS/" in text:
        return "data_constr"
    if mismatch:
        generated_tag = str(mismatch.get("generated_tag", "")).upper()
        golden_tag = str(mismatch.get("golden_tag", "")).upper()
        if "COM-SPEC" in generated_tag or "COM-SPEC" in golden_tag:
            return "com_spec"
        if "COMPU-METHOD" in generated_tag or "COMPU-METHOD" in golden_tag:
            return "compu_method"
        if "DATA-CONSTR" in generated_tag or "DATA-CONSTR" in golden_tag:
            return "data_constr"
    return "other"


def suggestion_for(category: str, diff_type: str) -> str:
    if category == "record_init_value":
        return "Add Record init value support: Excel row-level record fields -> RECORD-VALUE-SPECIFICATION."
    if category == "init_value":
        return "Align InitValue writer with DaVinci value spec shape, including CATEGORY/V/VT/VALUE handling."
    if category == "com_spec":
        if diff_type == "missing_in_generated":
            return "Check port naming, operation/data-element references, and optional ComSpec fields against golden."
        return "Compare ComSpec optional children and avoid writing fields DaVinci omits."
    if category == "compu_method":
        return "Align CompuMethod category, package path, UnitRef, and CompuScale representation."
    if category == "data_constr":
        return "Align DataConstr package path and internal/physical limits."
    return "Review whether this is expected scope difference or a writer/schema gap."


def summarize_element(element: etree._Element) -> dict[str, object]:
    tag = local_name(element)
    if tag.endswith("COM-SPEC"):
        return summarize_com_spec(element)
    if tag == "COMPU-METHOD":
        return summarize_compu_method(element)
    if tag == "DATA-CONSTR":
        return summarize_data_constr(element)
    return summarize_value_spec(element)


def summarize_com_spec(element: etree._Element) -> dict[str, object]:
    interesting_children = {
        "ALIVE-TIMEOUT",
        "CAN-INVALIDATE",
        "DATA-ELEMENT-REF",
        "ENABLE-UPDATE",
        "HANDLE-NEVER-RECEIVED",
        "HANDLE-OUT-OF-RANGE",
        "HANDLE-TIMEOUT-TYPE",
        "OPERATION-REF",
        "QUEUE-LENGTH",
        "USES-END-TO-END-PROTECTION",
    }
    summary: dict[str, object] = {"children": {}}
    for child in element:
        name = local_name(child)
        if name in interesting_children:
            summary["children"][name] = normalized_text(child)
        elif name in {"DATA-FILTER", "INIT-VALUE", "INVALID-VALUE"}:
            summary["children"][name] = summarize_subtree_shape(child)
    return summary


def summarize_compu_method(element: etree._Element) -> dict[str, object]:
    scales = []
    for scale in element.xpath(".//ar:COMPU-SCALE", namespaces=NS):
        scales.append(
            {
                "lower": first_text(scale, ".//ar:LOWER-LIMIT"),
                "upper": first_text(scale, ".//ar:UPPER-LIMIT"),
                "vt": first_text(scale, ".//ar:VT"),
                "v": [normalized_text(v) for v in scale.xpath(".//ar:COMPU-RATIONAL-COEFFS//ar:V", namespaces=NS)],
            }
        )
    return {
        "category": first_text(element, "./ar:CATEGORY"),
        "unit_ref": first_text(element, ".//ar:UNIT-REF"),
        "scales": scales,
    }


def summarize_data_constr(element: etree._Element) -> dict[str, object]:
    return {
        "internal_lower": first_text(element, ".//ar:INTERNAL-CONSTRS/ar:LOWER-LIMIT"),
        "internal_upper": first_text(element, ".//ar:INTERNAL-CONSTRS/ar:UPPER-LIMIT"),
        "physical_lower": first_text(element, ".//ar:PHYS-CONSTRS/ar:LOWER-LIMIT"),
        "physical_upper": first_text(element, ".//ar:PHYS-CONSTRS/ar:UPPER-LIMIT"),
    }


def summarize_value_spec(element: etree._Element) -> dict[str, object]:
    return summarize_subtree_shape(element)


def summarize_subtree_shape(element: etree._Element) -> dict[str, object]:
    return {
        "shape": [local_name(item) for item in element.iter()],
        "category": first_text(element, ".//ar:CATEGORY"),
        "values_v": [normalized_text(v) for v in element.xpath(".//ar:V", namespaces=NS)],
        "values_vt": [normalized_text(vt) for vt in element.xpath(".//ar:VT", namespaces=NS)],
        "values_value": [
            normalized_text(value)
            for value in element.xpath(".//ar:VALUE", namespaces=NS)
        ],
    }


def short_name_path(element: etree._Element) -> str:
    parts = []
    unnamed_tail = []
    current = element
    stack = []
    while current is not None:
        stack.append(current)
        current = current.getparent()
    stack.reverse()

    for item in stack:
        name = direct_short_name(item)
        if name:
            parts.append(name)
            unnamed_tail.clear()
        elif parts:
            tag = local_name(item)
            if tag not in {"AR-PACKAGES", "ELEMENTS", "PORTS", "PROVIDED-COM-SPECS", "REQUIRED-COM-SPECS"}:
                unnamed_tail.append(f"{tag}[{sibling_index(item)}]")
    if not parts:
        return ""
    return "/" + "/".join(parts + unnamed_tail)


def sibling_index(element: etree._Element) -> int:
    parent = element.getparent()
    if parent is None:
        return 1
    tag = local_name(element)
    index = 0
    for child in parent:
        if local_name(child) == tag:
            index += 1
        if child is element:
            return index
    return index


def direct_short_name(element: etree._Element) -> str:
    child = element.find("ar:SHORT-NAME", namespaces=NS)
    return normalized_text(child) if child is not None else ""


def first_text(element: etree._Element, xpath: str) -> str:
    found = element.xpath(xpath, namespaces=NS)
    if not found:
        return ""
    return normalized_text(found[0])


def normalized_text(element: etree._Element) -> str:
    return " ".join((element.text or "").split())


def local_name(element: etree._Element) -> str:
    return etree.QName(element).localname


def _counter_lines(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- {name}: {count}" for name, count in sorted(counter.items())]


def _section(title: str, values: Iterable[str]) -> list[str]:
    values = list(values)
    lines = [f"### {title}", ""]
    if not values:
        return lines + ["- none", ""]
    lines.extend(f"- `{value}`" for value in values[:50])
    if len(values) > 50:
        lines.append(f"- ... {len(values) - 50} more")
    lines.append("")
    return lines


def _mismatch_section(values: list[dict[str, object]]) -> list[str]:
    lines = ["### Summary Mismatches", ""]
    if not values:
        return lines + ["- none", ""]
    for item in values[:30]:
        lines.append(f"- `{item['path']}`")
        lines.append(f"  - generated tag: `{item['generated_tag']}`")
        lines.append(f"  - golden tag: `{item['golden_tag']}`")
        lines.append(f"  - generated: `{json.dumps(item['generated'], ensure_ascii=False)}`")
        lines.append(f"  - golden: `{json.dumps(item['golden'], ensure_ascii=False)}`")
    if len(values) > 30:
        lines.append(f"- ... {len(values) - 30} more")
    lines.append("")
    return lines


def _action_section(values: list[dict[str, str]]) -> list[str]:
    lines = ["### Prioritized Action Items", ""]
    if not values:
        return lines + ["- none", ""]
    lines.append("| Category | Diff Type | Path | Suggested Next Step |")
    lines.append("|---|---|---|---|")
    for item in values[:50]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(item["category"]),
                    _md(item["diff_type"]),
                    _md(f"`{item['path']}`"),
                    _md(item["suggestion"]),
                ]
            )
            + " |"
        )
    if len(values) > 50:
        lines.append(f"| ... | ... | ... | {len(values) - 50} more |")
    lines.append("")
    return lines


def _md(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", "<br>")


if __name__ == "__main__":
    raise SystemExit(main())

"""Validation engine — run all CORE-XXX rules against a WorkbookModel."""
from __future__ import annotations

from arxml_codegen.models.schema import WorkbookV2Model as WorkbookModel
from arxml_codegen.validator.finding import Finding
from arxml_codegen.validator.rules import (
    check_access_port_consistency,
    check_com_spec_semantics,
    check_compu_method_values,
    check_compu_scale_ranges,
    check_connector_consistency,
    check_cs_connectivity,
    check_cs_operation_arguments,
    check_cs_usage,
    check_dataconstr_coverage,
    check_datatype_completeness,
    check_datatype_mapping_completeness,
    check_datatype_reference_integrity,
    check_declared_port_usage,
    check_duplicate_names,
    check_init_value_types,
    check_linear_physical_range_consistency,
    check_port_interface_references,
    check_runnable_event_association,
    check_runnable_trigger_policy,
    check_record_structure,
    check_short_names,
    check_sr_connectivity,
    check_sr_multiplicity,
    check_sr_timing_relations,
    check_sr_usage,
    check_swc_completeness,
    check_timing_constraints,
    check_trigger_port_consistency,
    check_unit_references,
    check_unconnected_ports,
)

# All rules in order of execution
RULES = [
    ("CORE-050", "Naming & Identifiers", check_short_names),
    ("CORE-050", "Duplicate Detection", check_duplicate_names),
    ("CORE-010", "DataType Completeness", check_datatype_completeness),
    ("CORE-010", "DataType Reference Integrity", check_datatype_reference_integrity),
    ("CORE-010", "CompuMethod Values", check_compu_method_values),
    ("CORE-010", "CompuScale Ranges", check_compu_scale_ranges),
    ("CORE-010", "Linear Physical Range Consistency", check_linear_physical_range_consistency),
    ("CORE-010", "DataConstr Coverage", check_dataconstr_coverage),
    ("CORE-010", "Unit References", check_unit_references),
    ("CORE-010", "DataTypeMapping Completeness", check_datatype_mapping_completeness),
    ("CORE-010", "Record Structure", check_record_structure),
    ("CORE-010", "InitValue Types", check_init_value_types),
    ("CORE-010", "Port-Interface References", check_port_interface_references),
    ("CORE-010", "CS Operation Arguments", check_cs_operation_arguments),
    ("CORE-020", "SWC Completeness", check_swc_completeness),
    ("CORE-020", "Runnable-Event Association", check_runnable_event_association),
    ("CORE-024", "Runnable Trigger Policy", check_runnable_trigger_policy),
    ("CORE-025", "Port ComSpec Semantics", check_com_spec_semantics),
    ("CORE-040", "AccessPort Consistency", check_access_port_consistency),
    ("CORE-040", "Trigger Port Consistency", check_trigger_port_consistency),
    ("CORE-047", "Declared Port Usage", check_declared_port_usage),
    ("CORE-030", "Connector Consistency", check_connector_consistency),
    ("CORE-030", "Unconnected Ports", check_unconnected_ports),
    ("CORE-041", "SR Connectivity", check_sr_connectivity),
    ("CORE-042", "SR Usage", check_sr_usage),
    ("CORE-045", "SR Multiplicity", check_sr_multiplicity),
    ("CORE-043", "CS Connectivity", check_cs_connectivity),
    ("CORE-044", "CS Usage", check_cs_usage),
    ("CORE-060", "Timing Constraints", check_timing_constraints),
    ("CORE-060", "SR Timing Relations", check_sr_timing_relations),
]


def run_all(model: WorkbookModel) -> list[Finding]:
    """Execute all registered validation rules and return findings."""
    all_findings: list[Finding] = []
    for code_group, rule_name, rule_func in RULES:
        findings = rule_func(model)
        if findings:
            all_findings.extend(findings)
    return all_findings


def summarize(findings: list[Finding]) -> dict:
    """Return summary counts by severity and rule group."""
    by_severity = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    by_group: dict[str, int] = {}
    for f in findings:
        by_severity[f.severity.value] = by_severity.get(f.severity.value, 0) + 1
        group = f.code.split("-")[0] + "-" + f.code.split("-")[1] if "-" in f.code else f.code
        by_group[group] = by_group.get(group, 0) + 1
    return {"by_severity": by_severity, "by_group": by_group}

#!/usr/bin/env python3
"""Deterministically validate a mentor-task-interpreter v0.1 task specification."""
import argparse
import json
import re
import sys
from pathlib import Path


def resolve(root, reference):
    node = root
    for part in reference.removeprefix("#/").split("/"):
        node = node[part]
    return node


def type_matches(value, expected):
    return {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool), "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def validate(value, schema, root, path="$", errors=None):
    errors = [] if errors is None else errors
    if "$ref" in schema:
        return validate(value, resolve(root, schema["$ref"]), root, path, errors)
    expected = schema.get("type")
    if expected and not type_matches(value, expected):
        errors.append(f"{path}: expected {expected}")
        return errors
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0): errors.append(f"{path}: must not be empty")
        if "pattern" in schema and not re.match(schema["pattern"], value): errors.append(f"{path}: invalid format")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", value): errors.append(f"{path}: below minimum")
        if value > schema.get("maximum", value): errors.append(f"{path}: above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0): errors.append(f"{path}: too few items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value): validate(item, item_schema, root, f"{path}[{index}]", errors)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append(f"{path}: missing required field '{key}'")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties: errors.append(f"{path}: unknown field '{key}'")
        for key, child in value.items():
            if key in properties: validate(child, properties[key], root, f"{path}.{key}", errors)
    return errors


def referenced_ids(spec):
    references = []
    for section in ("deliverables", "explicit_requirements", "constraints", "deadlines", "dependencies", "execution_order", "clarifications"):
        for item in spec.get(section, []):
            references.extend(item.get("evidence_ids", item.get("related_evidence_ids", [])))
    for item in spec.get("inferences", []): references.extend(item.get("basis_evidence_ids", []))
    return references


def semantic_errors(spec):
    errors = []
    source_ids = [item["id"] for item in spec.get("input_sources", []) if "id" in item]
    evidence_ids = [item["id"] for item in spec.get("evidence", []) if "id" in item]
    for label, values in (("input source", source_ids), ("evidence", evidence_ids)):
        if len(values) != len(set(values)): errors.append(f"duplicate {label} IDs")
    for evidence in spec.get("evidence", []):
        if evidence.get("source_id") not in source_ids: errors.append(f"evidence {evidence.get('id')}: unknown source_id")
    for evidence_id in referenced_ids(spec):
        if evidence_id not in evidence_ids: errors.append(f"unknown evidence ID '{evidence_id}'")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_spec", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(__file__).parents[1] / "references" / "task-spec.schema.json")
    args = parser.parse_args()
    try:
        spec = json.loads(args.task_spec.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr); return 2
    errors = validate(spec, schema, schema) + semantic_errors(spec)
    if errors:
        print("INVALID:\n- " + "\n- ".join(errors), file=sys.stderr); return 1
    print(f"VALID: {args.task_spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

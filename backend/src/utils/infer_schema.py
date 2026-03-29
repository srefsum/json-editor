"""Infer a draft-07 JSON Schema from a single JSON value (sample instance)."""

from __future__ import annotations

import json
from typing import Any


def _schema_key(schema: dict[str, Any]) -> str:
    return json.dumps(schema, sort_keys=True)


def _merge_item_schemas(schemas: list[dict[str, Any]]) -> dict[str, Any]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for s in schemas:
        k = _schema_key(s)
        if k not in seen:
            seen.add(k)
            unique.append(s)
    if len(unique) == 1:
        return unique[0]
    return {"anyOf": unique}


def infer_json_schema(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, list):
        if not value:
            return {"type": "array", "items": {}}
        item_schemas = [infer_json_schema(item) for item in value]
        return {"type": "array", "items": _merge_item_schemas(item_schemas)}
    if isinstance(value, dict):
        if not value:
            return {"type": "object", "properties": {}, "additionalProperties": False}
        props = {k: infer_json_schema(v) for k, v in value.items()}
        return {
            "type": "object",
            "properties": props,
            "required": sorted(value.keys()),
            "additionalProperties": False,
        }
    return {}


def build_proposed_schema(sample: Any) -> dict[str, Any]:
    body = infer_json_schema(sample)
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        **body,
    }

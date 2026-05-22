#!/usr/bin/env python3
"""Tool call validation: allowlist check + parameter schema validation."""
import json
import yaml
import os
from pathlib import Path

ALLOWLIST_PATH = Path(__file__).parent.parent / "configs" / "tool_allowlist.yaml"

def load_allowlist():
    with open(ALLOWLIST_PATH) as f:
        return yaml.safe_load(f)["tools"]

def find_tool(name: str, allowlist: list):
    for tool in allowlist:
        if tool["name"] == name:
            return tool
    return None

def validate_tool_call(tool_name: str, parameters: dict, role: str = "user"):
    """
    Returns (is_allowed: bool, error_message: str or None).
    """
    allowlist = load_allowlist()
    tool = find_tool(tool_name, allowlist)
    if tool is None:
        return False, f"Tool '{tool_name}' is not in allowlist."

    # Permission level check
    if tool["permission_level"] == "write" and "allowed_roles" in tool:
        if role not in tool["allowed_roles"]:
            return False, f"Role '{role}' not allowed for tool '{tool_name}'."

    # Parameter type check
    if not isinstance(parameters, dict):
        return False, f"Parameters must be a dictionary, got {type(parameters).__name__}."

    # Schema validation
    schema = tool.get("input_schema", {})
    if schema:
        try:
            _validate_schema(parameters, schema)
        except ValueError as e:
            return False, f"Parameter validation failed: {e}"

    return True, None

def _validate_schema(params: dict, schema: dict):
    """Basic recursive schema validation."""
    required = schema.get("required", [])
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    for field, value in params.items():
        props = schema.get("properties", {})
        if field not in props:
            continue
        field_schema = props[field]
        ftype = field_schema.get("type")
        if ftype == "array":
            if not isinstance(value, list):
                raise ValueError(f"Field '{field}' should be array")
            items_type = field_schema.get("items", {}).get("type")
            if items_type and not all(isinstance(x, (int, float)) for x in value):
                raise ValueError(f"Array items should be {items_type}")
            minItems = field_schema.get("minItems")
            maxItems = field_schema.get("maxItems")
            if minItems and len(value) < minItems:
                raise ValueError(f"Array too short (min {minItems})")
            if maxItems and len(value) > maxItems:
                raise ValueError(f"Array too long (max {maxItems})")
        elif ftype == "string":
            if not isinstance(value, str):
                raise ValueError(f"Field '{field}' should be string")
            pattern = field_schema.get("pattern")
            if pattern:
                import re
                if not re.match(pattern, value):
                    raise ValueError(f"Field '{field}' does not match pattern {pattern}")
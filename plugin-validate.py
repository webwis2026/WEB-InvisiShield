#!/usr/bin/env python3
"""
零改造引擎插件配置校验脚本
1. JSON Schema 结构校验（需安装 jsonschema: pip install jsonschema）
2. 自定义业务规则校验（插件顺序、禁止项等）

使用: python plugin-validate.py <config.json>
"""

import json
import sys
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_plugin_name(item):
    return item if isinstance(item, str) else (item.get("name") if isinstance(item, dict) else None)


def validate_custom_rules(data):
    """自定义业务规则校验，返回错误列表"""
    errors = []
    gw = data.get("gw_configures")
    if not gw:
        return errors

    plugins = gw.get("plugins") or []
    exposure_auth_idx = next(
        (i for i, p in enumerate(plugins) if get_plugin_name(p) == "exposure_auth"),
        -1,
    )

    if exposure_auth_idx >= 0:
        before_auth = [get_plugin_name(p) for p in plugins[:exposure_auth_idx]]
        if "uri_blocker" not in before_auth:
            errors.append({
                "rule": "plugin_order",
                "message": "uri_blocker 必须在 exposure_auth 之前",
                "path": "gw_configures.plugins",
            })
        if "request_blocker" not in before_auth:
            errors.append({
                "rule": "plugin_order",
                "message": "request_blocker 必须在 exposure_auth 之前",
                "path": "gw_configures.plugins",
            })
        if "uri_bypass" not in before_auth:
            errors.append({
                "rule": "plugin_order",
                "message": "uri_bypass 必须在 exposure_auth 之前",
                "path": "gw_configures.plugins",
            })

    if any(get_plugin_name(p) == "regex_whiteuri" for p in plugins):
        errors.append({
            "rule": "forbidden",
            "message": "禁止使用 regex_whiteuri，请改用 uri_bypass",
            "path": "gw_configures.plugins",
        })

    for name in ("exposure_session", "exposure_user"):
        if any(get_plugin_name(p) == name for p in plugins):
            errors.append({
                "rule": "forbidden",
                "message": f"{name} 必须在 plugin_confs 中配置，不得在主 plugins 数组",
                "path": "gw_configures.plugins",
            })

    for i, sr in enumerate(gw.get("sub_routes") or []):
        if sr.get("plugin_group_id") and not sr.get("plugins"):
            errors.append({
                "rule": "deprecated",
                "message": f"sub_routes[{i}] 使用 plugin_group_id，新规范建议使用内联 plugins",
                "path": f"gw_configures.sub_routes[{i}]",
            })

    if gw.get("plugin_groups"):
        errors.append({
            "rule": "forbidden",
            "message": "plugin_groups 已废弃，请使用子路由内联 plugins",
            "path": "gw_configures.plugin_groups",
        })

    return errors


def validate_schema(data, schema_path):
    """JSON Schema 校验，返回错误列表，空列表表示通过"""
    try:
        import jsonschema
    except ImportError:
        print("Note: pip install jsonschema for schema validation", file=sys.stderr)
        return []

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(data, schema)
        return []
    except jsonschema.ValidationError as e:
        return [str(e)]


def main():
    if len(sys.argv) < 2:
        print("Usage: python plugin-validate.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1]).resolve()
    if not config_path.exists():
        print(f"File not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = load_json(str(config_path))
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    schema_path = Path(__file__).parent / "plugin-config.schema.json"

    all_errors = []

    # 自定义规则
    custom_errors = validate_custom_rules(data)
    all_errors.extend(custom_errors)

    # JSON Schema
    if schema_path.exists():
        schema_errors = validate_schema(data, schema_path)
        for m in schema_errors:
            all_errors.append({"rule": "schema", "message": m, "path": ""})
    else:
        print("Warning: plugin-config.schema.json not found, skip schema validation")

    if all_errors:
        print("Validation failed:\n", file=sys.stderr)
        for e in all_errors:
            msg = e.get("message", e) if isinstance(e, dict) else e
            path = e.get("path", "")
            print(f"  [{e.get('rule', 'error')}] {path}: {msg}", file=sys.stderr)
        sys.exit(1)

    print("Validation passed.")


if __name__ == "__main__":
    main()

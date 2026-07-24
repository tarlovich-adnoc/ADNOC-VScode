#!/usr/bin/env python3
"""Create a secret-safe Rider/Copilot MCP mirror from .vscode/mcp.json."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


INPUT_PLACEHOLDER = re.compile(r"^\$\{input:[^}]+}$")


def strip_jsonc(raw: str) -> str:
    """Strip the full-line and block comments supported by this repository."""
    raw = raw.lstrip("\ufeff")
    raw = re.sub(r"^\s*//[^\n]*$", "", raw, flags=re.MULTILINE)
    return re.sub(r"/\*[\s\S]*?\*/", "", raw)


def load_jsonc(path: Path) -> dict[str, Any]:
    value = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def rider_config(vscode: dict[str, Any]) -> dict[str, Any]:
    """Convert VS Code MCP configuration to the shared Rider-safe schema."""
    servers = vscode.get("servers")
    if not isinstance(servers, dict) or not servers:
        raise ValueError('.vscode/mcp.json must contain a non-empty "servers" object')

    mirrored = copy.deepcopy(servers)
    for server in mirrored.values():
        if not isinstance(server, dict):
            continue
        env = server.get("env")
        if not isinstance(env, dict):
            continue
        safe_env = {
            key: value
            for key, value in env.items()
            if not (isinstance(value, str) and INPUT_PLACEHOLDER.fullmatch(value))
        }
        if safe_env:
            server["env"] = safe_env
        else:
            server.pop("env", None)
    return {"servers": mirrored}


def sync(root: Path) -> tuple[str, Path]:
    source = root / ".vscode" / "mcp.json"
    target = root / ".mcp.json"
    if not source.is_file():
        raise FileNotFoundError(f"missing {source}")

    expected = rider_config(load_jsonc(source))
    existed = target.is_file()
    if existed:
        try:
            if load_jsonc(target) == expected:
                return "unchanged", target
        except (OSError, ValueError, json.JSONDecodeError):
            pass

    target.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "updated" if existed else "created", target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        state, _ = sync(args.root.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[FAIL] rider mcp sync - {exc}")
        return 1
    if state == "unchanged":
        print("[PASS] rider mcp sync - .mcp.json already matches .vscode/mcp.json")
    else:
        print(f"[FIXED] rider mcp sync - {state} .mcp.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

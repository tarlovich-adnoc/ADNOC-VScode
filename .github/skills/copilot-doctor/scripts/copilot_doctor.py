#!/usr/bin/env python3
"""Deterministically diagnose and repair the local repository Copilot workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from sync_rider_mcp import load_jsonc, sync


SETTINGS_LOCATIONS = {
    "chat.agentSkillsLocations": [
        ".github/skills/generic",
        ".github/skills/ba",
        ".github/skills/qa",
        ".github/skills/pm",
        ".github/skills/designer",
        ".github/skills/devops",
        ".github/skills/optional",
        ".github/skills/team-local",
    ],
    "chat.agentFilesLocations": [
        ".github/agents/generic",
        ".github/agents/ba",
        ".github/agents/qa",
        ".github/agents/pm",
        ".github/agents/devops",
        ".github/agents/designer",
        ".github/agents/team-local",
    ],
    "chat.promptFilesLocations": [
        ".github/prompts",
        ".github/prompts/generic",
        ".github/prompts/ba",
        ".github/prompts/qa",
        ".github/prompts/devops",
        ".github/prompts/pm",
        ".github/prompts/designer",
        ".github/prompts/optional",
        ".github/prompts/team-local",
    ],
    "chat.hookFilesLocations": [
        ".github/hooks/generic",
        ".github/hooks/ba",
        ".github/hooks/qa",
        ".github/hooks/devops",
        ".github/hooks/pm",
        ".github/hooks/designer",
        ".github/hooks/optional",
        ".github/hooks/team-local",
    ],
}

VALIDATORS = [
    "validate-frontmatter.js",
    "validate-skills.js",
    "validate-no-personal-paths.js",
    "check-unicode-safety.js",
    "validate-no-secrets.js",
]


def rerun_command(ide: str) -> str:
    selected = ide if ide in {"vscode", "rider"} else "auto"
    return f"python3 .github/skills/copilot-doctor/scripts/copilot_doctor.py --ide {selected}"


def copier_update_fixes(ide: str) -> list[str]:
    return [
        "Verify Copier is available:\npython3 -m copier --version\nIf that fails, install it with:\npython3 -m pip install --user \"copier>=9,<10\"",
        "From the repository root, restore template-managed files:\npython3 -m copier update --defaults",
        "Resolve every reported merge conflict without deleting project-specific changes, then rerun:\n" + rerun_command(ide),
    ]


def passport_fixes(source: str | None, ide: str) -> list[str]:
    current = source if source is not None else "<missing>"
    return [
        "Obtain the canonical HTTPS or SSH clone URL and template release/tag from the team that owns this repository template. Do not use a local path such as ./ or /Users/... .",
        "Open .copier-answers.yml at the repository root. Set _commit to the template release/tag and set _src_path to one of these remote Git forms, replacing the placeholders:\nHTTPS: _src_path: https://<git-host>/<group>/<template-repository>.git\nSSH: _src_path: git@<git-host>:<group>/<template-repository>.git\nCopier-prefixed HTTPS or SSH is also supported: git+https://... or git+ssh://...",
        f"Replace _src_path only if it is missing, local, or malformed (current value: {current}). Save .copier-answers.yml without changing project answers such as team_name, stack, or azure_org.",
        "Verify the passport and preview the update:\npython3 -m copier update --defaults --pretend",
        "If the preview uses the expected template and release, apply it:\npython3 -m copier update --defaults",
        "Resolve any merge conflicts, then rerun:\n" + rerun_command(ide),
    ]


@dataclass
class Check:
    status: str
    name: str
    detail: str
    fixes: list[str] = field(default_factory=list)


def run(command: list[str], root: Path, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def passport_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", raw)
        if match:
            values[match.group(1)] = match.group(2).strip("'\"")
    return values


def is_remote_git_source(source: str) -> bool:
    """Return whether source is a Copier-compatible HTTPS or SSH Git URL."""
    if not source or re.search(r"\s", source):
        return False

    # Git's SCP-like SSH syntax has no URI scheme. Copier recognizes git@ URLs directly.
    if re.fullmatch(r"git@[^/:]+:[^:]+", source):
        return True

    copier_prefixed = source.startswith("git+")
    try:
        parsed = urlsplit(source[4:] if copier_prefixed else source)
        hostname = parsed.hostname
    except ValueError:
        return False
    if parsed.scheme not in {"https", "ssh"} or not hostname:
        return False
    if not parsed.path or parsed.path == "/":
        return False

    # The git+ prefix forces Copier to treat a URL as Git. Without it, a .git suffix is
    # required for arbitrary enterprise hosts such as git.epam.com.
    return copier_prefixed or source.endswith(".git")


def initialize_git(root: Path) -> tuple[Check, bool]:
    if shutil.which("git") is None:
        return Check("FAIL", "repo + git", "git is not installed or not on PATH", ["Install Git, reopen the terminal, and rerun copilot-doctor."]), False
    status = run(["git", "rev-parse", "--is-inside-work-tree"], root)
    if status.returncode == 0 and status.stdout.strip() == "true":
        return Check("PASS", "repo + git", "local Git work tree is initialized"), False
    created = run(["git", "init", "-b", "main"], root)
    if created.returncode != 0:
        created = run(["git", "init"], root)
    if created.returncode != 0:
        detail = (created.stderr or created.stdout).strip()[-400:]
        return Check("FAIL", "repo + git", f"git init failed: {detail}", ["Fix the reported Git error and rerun copilot-doctor."]), False
    return Check("FIXED", "repo + git", "initialized a local Git repository; initial commit will be created after checks"), True


def check_passport(root: Path, passport: dict[str, str], ide: str) -> Check:
    missing = [key for key in ("_commit", "_src_path") if not passport.get(key)]
    if missing:
        return Check("FAIL", "copier passport", "missing " + ", ".join(missing), passport_fixes(passport.get("_src_path"), ide))
    source = passport["_src_path"]
    if not is_remote_git_source(source):
        return Check(
            "FAIL",
            "copier passport",
            f"_src_path is not a supported remote Git URL: {source}",
            passport_fixes(source, ide),
        )
    return Check("PASS", "copier passport", f"src: {source}; template: {passport['_commit']}")


def repair_settings(root: Path) -> Check:
    path = root / ".vscode" / "settings.json"
    created = not path.exists()
    try:
        settings = load_jsonc(path) if path.exists() else {}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return Check("FAIL", "vscode settings", f"cannot parse .vscode/settings.json: {exc}", ["Fix the JSON/JSONC syntax, then rerun copilot-doctor; the doctor will add only missing canonical entries."])

    changes: list[str] = []
    if settings.get("github.copilot.chat.codeGeneration.useInstructionFiles") is not True:
        settings["github.copilot.chat.codeGeneration.useInstructionFiles"] = True
        changes.append("github.copilot.chat.codeGeneration.useInstructionFiles")
    for registry, locations in SETTINGS_LOCATIONS.items():
        actual = settings.get(registry)
        if not isinstance(actual, dict):
            actual = {}
            settings[registry] = actual
        for location in locations:
            if actual.get(location) is not True:
                actual[location] = True
                changes.append(f"{registry}.{location}")
    if not changes:
        return Check("PASS", "vscode settings", "instruction loading and all four location registries are complete")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    action = "created .vscode/settings.json" if created else f"added {len(changes)} missing entry/entries"
    return Check("FIXED", "vscode settings", action)


def detect_ide(requested: str, root: Path) -> str:
    if requested != "auto":
        return requested
    markers = " ".join(f"{key}={value}" for key, value in os.environ.items() if key in {"JETBRAINS_IDE", "RIDER", "IDEA_INITIAL_DIRECTORY"})
    return "rider" if (root / ".idea").exists() or markers else "unknown"


def operating_system() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return system or "unknown"


def repair_rider(root: Path, ide: str) -> Check:
    if ide != "rider":
        detail = "VS Code selected" if ide == "vscode" else "IDE not detected; rerun with --ide rider when using Rider"
        return Check("SKIP", "rider mcp mirror", detail)
    try:
        state, _ = sync(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return Check(
            "FAIL",
            "rider mcp mirror",
            str(exc),
            [
                "Open .vscode/mcp.json and correct the JSON/JSONC syntax reported above. Do not insert literal access tokens.",
                "Regenerate the Rider mirror:\npython3 .github/skills/copilot-doctor/scripts/sync_rider_mcp.py",
                "Confirm the repository-root .mcp.json contains the same servers as .vscode/mcp.json and contains no ${input:...} placeholders, then rerun:\n" + rerun_command("rider"),
            ],
        )
    status = "PASS" if state == "unchanged" else "FIXED"
    return Check(status, "rider mcp mirror", ".mcp.json already correct" if state == "unchanged" else f"{state} root .mcp.json from .vscode/mcp.json")


def check_artifacts(root: Path, passport: dict[str, str], ide: str) -> Check:
    errors: list[str] = []
    generic = root / ".github" / "instructions" / "generic"
    instructions = generic / "adnoc-standard.instructions.md"
    team = passport.get("team_name", "")
    if not instructions.is_file() or team not in instructions.read_text(encoding="utf-8"):
        errors.append("adnoc-standard.instructions.md is missing or does not contain team_name")
    if not (generic / "project-learnings.instructions.md").is_file():
        errors.append("project-learnings.instructions.md is missing")
    stack = passport.get("stack")
    if stack and stack != "none":
        stack_file = "react.instructions.md" if stack == "react-web" else f"{stack}.instructions.md"
        if not (generic / stack_file).is_file():
            errors.append(f"{stack_file} is missing")
    for path in (root / ".github" / "instructions").rglob("*.instructions.md"):
        if not re.search(r"(?m)^applyTo:\s*", path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(root)} has no applyTo")
    if not (root / ".github" / "agents" / "generic" / "code-reviewer.agent.md").is_file():
        errors.append("code-reviewer.agent.md is missing")
    required_prompts = ["ado-intake", "explain", "fix-bug", "git-deliver", "migrate-to-standard", "refactor", "selfimprove"]
    for name in required_prompts:
        if not (root / ".github" / "prompts" / "generic" / f"{name}.prompt.md").is_file():
            errors.append(f"{name}.prompt.md is missing")
    if not (root / ".github" / "skills" / "copilot-doctor" / "SKILL.md").is_file():
        errors.append("copilot-doctor skill is missing")
    if errors:
        return Check("FAIL", "artifact layout", "; ".join(errors), copier_update_fixes(ide))
    agent_count = len(list((root / ".github" / "agents").rglob("*.agent.md")))
    prompt_count = len(list((root / ".github" / "prompts").rglob("*.prompt.md")))
    skill_count = len(list((root / ".github" / "skills").rglob("SKILL.md")))
    return Check("PASS", "artifact layout", f"agents: {agent_count}, prompts: {prompt_count}, skills: {skill_count}")


def run_validators(root: Path) -> tuple[Check, bool]:
    if shutil.which("node") is None:
        return Check("FAIL", "gate", "node is not installed; no validators ran", ["Install the approved Node.js LTS release, reopen the terminal, and rerun copilot-doctor."]), False
    passed = 0
    failures: list[str] = []
    secrets_safe = False
    for validator in VALIDATORS:
        path = root / ".github" / "ci-validators" / validator
        if not path.is_file():
            failures.append(f"missing {validator}")
            continue
        try:
            result = run(["node", str(path)], root, 45)
        except subprocess.TimeoutExpired:
            failures.append(f"{validator} timed out")
            continue
        if result.returncode == 0:
            passed += 1
            if validator == "validate-no-secrets.js":
                secrets_safe = True
        else:
            lines = [line.strip() for line in (result.stderr or result.stdout).splitlines() if line.strip()]
            failures.append(f"{validator}: {lines[-1] if lines else f'exit {result.returncode}'}")
    if failures:
        commands = "\n".join(f"node .github/ci-validators/{validator}" for validator in VALIDATORS)
        total = len(VALIDATORS)
        return Check(
            "FAIL",
            "gate",
            f"{passed}/{total} green; " + "; ".join(failures),
            [
                "Run every validator separately from the repository root so each complete error is visible:\n" + commands,
                "Fix the files named by each failing validator. Do not disable a validator or add a secret/path exception merely to make the gate pass.",
                "Run every command again and confirm each exits successfully, then rerun copilot-doctor.",
            ],
        ), secrets_safe
    total = len(VALIDATORS)
    return Check("PASS", "gate", f"{total}/{total} local validators green"), secrets_safe


def append_telemetry(root: Path, ok: bool) -> Check:
    target = root / "ai" / "governance" / "agent-runs.jsonl"
    record = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "agent": "copilot-doctor",
        "round": 1,
        "inTok": 0,
        "outTok": 0,
        "costUsd": 0.0,
        "model": "copilot",
        "ok": ok,
        "workflow": "copilot-health-check",
        "repo": root.name,
        "skills": ["copilot-doctor"],
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError as exc:
        return Check("FAIL", "telemetry", f"could not append telemetry: {exc}", ["Fix file permissions for ai/governance/agent-runs.jsonl and rerun copilot-doctor."])
    return Check("PASS", "telemetry", "appended one copilot-doctor record")


def create_initial_commit(root: Path, required: bool, secrets_safe: bool) -> Check:
    if not required:
        return Check("SKIP", "initial commit", "repository already had Git initialized")
    if not secrets_safe:
        return Check("FAIL", "initial commit", "not created because validate-no-secrets did not pass", ["Remove any detected secret, rerun copilot-doctor, and let it create the initial commit."])
    added = run(["git", "add", "-A"], root)
    if added.returncode != 0:
        return Check("FAIL", "initial commit", (added.stderr or added.stdout).strip()[-400:], ["Fix the Git staging error and rerun copilot-doctor."])
    commit = run(
        [
            "git",
            "-c",
            "user.name=Copilot Doctor",
            "-c",
            "user.email=copilot-doctor@local.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "chore: initialize repository with Copilot workflow",
        ],
        root,
    )
    if commit.returncode != 0:
        return Check("FAIL", "initial commit", (commit.stderr or commit.stdout).strip()[-400:], ["Fix the reported Git commit error and rerun copilot-doctor; staged files were preserved."])
    head = run(["git", "rev-parse", "--short", "HEAD"], root)
    return Check("FIXED", "initial commit", f"created {head.stdout.strip()}")


def manual_notes(root: Path, ide: str) -> list[Check]:
    notes = [
        Check("NOTE", "ide", f"{ide} sign-in, Agent mode, plugin version and workspace trust are IDE-only states and were not checked"),
    ]
    learning = root / ".github" / "instructions" / "generic" / "project-learnings.instructions.md"
    if learning.is_file():
        lines = len(learning.read_text(encoding="utf-8").splitlines())
        if lines > 150:
            notes.append(Check("NOTE", "project learnings", f"{lines} lines; graduate reusable rule clusters into a focused skill and prune this always-loaded file"))
    return notes


def print_report(checks: list[Check], passport: dict[str, str], ide: str = "unknown") -> None:
    team = passport.get("team_name", "unknown-team")
    commit = passport.get("_commit", "unknown-template")
    print(f"COPILOT DOCTOR LOCAL - {team} @ {commit}")
    print(f"CONTEXT: os={operating_system()}; ide={ide}")
    for check in checks:
        print(f"[{check.status}] {check.name} - {check.detail}")
        if check.fixes:
            print("       fix:")
            for index, fix in enumerate(check.fixes, 1):
                lines = fix.splitlines() or [""]
                print(f"       {index}. {lines[0]}")
                for line in lines[1:]:
                    print(f"          {line}")
    failures = sum(check.status == "FAIL" for check in checks)
    fixed = sum(check.status == "FIXED" for check in checks)
    if failures:
        print(f"LOCAL VERDICT: {failures} fix(es) needed; {fixed} deterministic repair(s) applied.")
    else:
        print(f"LOCAL VERDICT: healthy; {fixed} deterministic repair(s) applied.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ide", choices=("auto", "vscode", "rider"), default="auto")
    args = parser.parse_args()
    root = args.root.resolve()
    passport = passport_values(root / ".copier-answers.yml")
    ide = detect_ide(args.ide, root)
    checks: list[Check] = []

    git_check, initial_commit_required = initialize_git(root)
    checks.extend([repair_settings(root), git_check, check_passport(root, passport, ide), repair_rider(root, ide)])
    checks.append(check_artifacts(root, passport, ide))
    gate_check, secrets_safe = run_validators(root)
    checks.append(gate_check)
    telemetry = append_telemetry(root, not any(check.status == "FAIL" for check in checks))
    checks.append(telemetry)
    checks.append(create_initial_commit(root, initial_commit_required, secrets_safe))
    checks.extend(manual_notes(root, ide))
    print_report(checks, passport, ide)
    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())

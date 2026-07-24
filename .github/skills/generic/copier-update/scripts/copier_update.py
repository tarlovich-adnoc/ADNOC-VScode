#!/usr/bin/env python3
"""Safely update a Git repository from its Copier template.

The script is intentionally dependency-free and shell-independent so the same workflow runs on
macOS and Windows. It preserves a dirty worktree in a named stash, commits only the template update,
and restores the stash before reporting success.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


INSTALL_REQUIRED = 3
BLOCKED = 4


class WorkflowError(RuntimeError):
    """A safe, user-actionable workflow failure."""


def run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise WorkflowError(f"Command failed: {' '.join(args)}\n{detail}")
    return result


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], root, check=check)


def output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout.strip()


def git_epam_connection_advice(detail: str) -> str | None:
    """Return user guidance for GitLab transport failures that Zscaler can cause."""
    normalized = detail.casefold()
    if "git.epam.com" not in normalized:
        return None

    transport_markers = (
        "could not resolve host",
        "could not resolve hostname",
        "failed to connect",
        "connection refused",
        "connection reset",
        "connection timed out",
        "operation timed out",
        "timed out",
        "network is unreachable",
        "no route to host",
        "ssl certificate",
        "certificate verify failed",
        "unable to get local issuer certificate",
        "self-signed certificate",
        "secure channel",
        "schannel",
        "tls",
        "proxy",
    )
    if not any(marker in normalized for marker in transport_markers):
        return None

    return (
        "Connection to git.epam.com failed because of a network/VPN, proxy, TLS, or certificate "
        "problem. Connect to EPAM's network or VPN, then rerun the update. "
        "You might need to disable Zscaler."
    )


def version_tuple(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def supported_versions(root: Path) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    minimum = (9, 0, 0)
    maximum = (9, 99, 99)
    contract = root / ".github" / "tested-copier-versions.txt"
    if not contract.exists():
        return minimum, maximum

    values: dict[str, tuple[int, int, int]] = {}
    for line in contract.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(min|max):\s*['\"]?([^'\"\s]+)", line.strip())
        if match:
            parsed = version_tuple(match.group(2))
            if parsed:
                values[match.group(1)] = parsed
    return values.get("min", minimum), values.get("max", maximum)


def copier_version(root: Path) -> tuple[str | None, tuple[int, int, int] | None]:
    executable = shutil.which("copier")
    if not executable:
        return None, None
    result = run([executable, "--version"], root, check=False)
    text = (result.stdout or result.stderr).strip()
    return text or None, version_tuple(text)


def in_progress_operations(root: Path) -> list[str]:
    operations: list[str] = []
    for name, label in (
        ("MERGE_HEAD", "merge"),
        ("rebase-merge", "rebase"),
        ("rebase-apply", "rebase"),
        ("CHERRY_PICK_HEAD", "cherry-pick"),
    ):
        path_text = output(git(root, "rev-parse", "--git-path", name))
        path = Path(path_text)
        if not path.is_absolute():
            path = root / path
        if path.exists() and label not in operations:
            operations.append(label)
    return operations


def unique_update_branch(root: Path) -> str:
    base = "copier-update/" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = base
    suffix = 2
    while git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}", check=False).returncode == 0:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def create_recovery_stash(root: Path) -> tuple[str | None, str | None]:
    if not output(git(root, "status", "--porcelain")):
        return None, None

    message = "copier-update checkpoint " + dt.datetime.now(dt.timezone.utc).isoformat()
    git(root, "stash", "push", "--include-untracked", "--message", message)
    stash_ref = "stash@{0}"
    stash_oid = output(git(root, "rev-parse", stash_ref))
    if output(git(root, "status", "--porcelain")):
        raise WorkflowError(
            f"Could not make the working tree clean. Recovery stash retained: {stash_ref} ({stash_oid})."
        )
    return stash_ref, stash_oid


def restore_recovery_stash(root: Path, stash_ref: str | None, stash_oid: str | None) -> bool:
    if not stash_ref:
        return False
    applied = git(root, "stash", "apply", "--index", stash_ref, check=False)
    if applied.returncode != 0:
        detail = (applied.stderr or applied.stdout).strip()
        raise WorkflowError(
            "The template update is committed, but unfinished work could not be restored cleanly.\n"
            f"Recovery stash retained: {stash_ref} ({stash_oid}).\n{detail}"
        )
    git(root, "stash", "drop", stash_ref)
    return True


def template_version(root: Path) -> str:
    answers = root / ".copier-answers.yml"
    for line in answers.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^_commit:\s*['\"]?([^'\"\s]+)", line.strip())
        if match:
            return match.group(1)
    return "unknown"


def append_telemetry(root: Path) -> None:
    telemetry = root / "ai" / "governance" / "agent-runs.jsonl"
    telemetry.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "agent": "copier-update",
        "round": 1,
        "inTok": 0,
        "outTok": 0,
        "costUsd": 0.0,
        "model": "copilot",
        "ok": True,
        "workflow": "template-update",
        "repo": root.name,
        "skills": ["copier-update"],
    }
    with telemetry.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def preflight(root: Path) -> dict[str, object]:
    operations = in_progress_operations(root)
    if operations:
        raise WorkflowError(f"Git operation already in progress: {', '.join(operations)}.")

    answers = root / ".copier-answers.yml"
    if not answers.exists():
        raise WorkflowError(".copier-answers.yml is missing; this repository is not linked to a Copier template.")

    user_name = output(git(root, "config", "user.name", check=False))
    user_email = output(git(root, "config", "user.email", check=False))
    missing = [name for name, value in (("user.name", user_name), ("user.email", user_email)) if not value]
    if missing:
        raise WorkflowError("Missing local Git identity: " + ", ".join(missing) + ".")

    minimum, maximum = supported_versions(root)
    copier_text, copier_parsed = copier_version(root)
    branch = output(git(root, "branch", "--show-current")) or "detached HEAD"
    upstream_result = git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{u}",
        check=False,
    )
    upstream = output(upstream_result) if upstream_result.returncode == 0 else None
    return {
        "branch": branch,
        "dirty": bool(output(git(root, "status", "--porcelain"))),
        "upstream": upstream,
        "copier_text": copier_text,
        "copier_version": copier_parsed,
        "minimum": minimum,
        "maximum": maximum,
    }


def print_preflight(root: Path, state: dict[str, object]) -> None:
    minimum = ".".join(str(part) for part in state["minimum"])
    maximum = ".".join(str(part) for part in state["maximum"])
    print("Prerequisite checks")
    print(f"  PASS  Git repository       {root}")
    print("  PASS  Git operation        none")
    print(f"  INFO  Current branch       {state['branch']}")
    print(f"  INFO  Working tree         {'unfinished work found' if state['dirty'] else 'clean'}")
    print(f"  INFO  Remote tracking      {state['upstream'] or 'not set'}")
    print(f"  INFO  Copier supported     {minimum} through {maximum}")
    print(f"  INFO  Copier installed     {state['copier_text'] or 'missing'}")
    print("  PASS  Copier passport      .copier-answers.yml found")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository path; defaults to the current directory")
    parser.add_argument("--reanswer", action="store_true", help="Allow Copier to ask template questions again")
    parser.add_argument("--push", action="store_true", help="Push the update branch after local completion")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested = Path(args.repo).resolve()
    stash_ref: str | None = None
    stash_oid: str | None = None
    try:
        root_text = output(run(["git", "-C", str(requested), "rev-parse", "--show-toplevel"], requested))
        root = Path(root_text).resolve()
        state = preflight(root)
        print_preflight(root, state)

        version = state["copier_version"]
        minimum = state["minimum"]
        maximum = state["maximum"]
        if version is None or version < minimum or version > maximum:
            reason = state["copier_text"] or "Copier is not installed"
            print(f"INSTALL_REQUIRED: {reason}; invoke ai-sdlc-template-install, then rerun this helper.")
            return INSTALL_REQUIRED

        original_branch = state["branch"]
        original_upstream = state["upstream"]
        stash_ref, stash_oid = create_recovery_stash(root)

        current = output(git(root, "branch", "--show-current"))
        if not current.startswith("copier-update/"):
            current = unique_update_branch(root)
            git(root, "switch", "-c", current)

        command = [shutil.which("copier") or "copier", "update"]
        if not args.reanswer:
            command.append("--defaults")
        update = run(command, root, check=False)
        if update.stdout:
            print(update.stdout.rstrip())
        if update.returncode != 0:
            detail = (update.stderr or update.stdout).strip()
            connection_advice = git_epam_connection_advice(detail)
            if connection_advice:
                detail = f"{detail}\n{connection_advice}"
            raise WorkflowError(
                "Copier update failed. The recovery stash has not been deleted.\n"
                f"Recovery stash: {stash_ref or 'not needed'} ({stash_oid or 'n/a'}).\n{detail}"
            )

        conflicts = output(git(root, "diff", "--name-only", "--diff-filter=U"))
        if conflicts:
            raise WorkflowError(
                "Copier update produced conflicts. The recovery stash has not been deleted.\n"
                f"Conflicting files:\n{conflicts}\nRecovery stash: {stash_ref or 'not needed'} ({stash_oid or 'n/a'})."
            )

        changed_before_telemetry = output(git(root, "status", "--short"))
        append_telemetry(root)
        git(root, "add", "-A")
        version_label = template_version(root)
        git(root, "commit", "-m", f"chore: copier update to template {version_label}")
        commit = output(git(root, "rev-parse", "--short", "HEAD"))

        restored = restore_recovery_stash(root, stash_ref, stash_oid)

        pushed = False
        if args.push:
            upstream = git(
                root,
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{u}",
                check=False,
            )
            if upstream.returncode == 0:
                git(root, "push")
            else:
                remote = (str(original_upstream).split("/", 1)[0] if original_upstream else "origin")
                if git(root, "remote", "get-url", remote, check=False).returncode != 0:
                    raise WorkflowError("Update committed locally, but no suitable Git remote exists for --push.")
                git(root, "push", "--set-upstream", remote, current)
            pushed = True

        print("\nTemplate update complete")
        print(f"  Update branch: {current}")
        print(f"  Template version: {version_label}")
        print(f"  Update commit: {commit}")
        print(f"  Template changes: {'yes' if changed_before_telemetry else 'no; telemetry recorded'}")
        print(f"  Unfinished work: {'restored' if restored else 'none was present'}")
        print(f"  Push: {'completed' if pushed else 'not requested; branch is local'}")
        if original_branch != current:
            print(f"  Started from: {original_branch}")
        return 0
    except (WorkflowError, OSError) as exc:
        message = str(exc)
        if stash_ref and stash_ref not in message:
            message += f"\nRecovery stash retained: {stash_ref} ({stash_oid})."
        print(f"BLOCKED: {message}", file=sys.stderr)
        return BLOCKED


if __name__ == "__main__":
    raise SystemExit(main())

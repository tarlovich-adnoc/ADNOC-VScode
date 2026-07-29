---
name: ai-sdlc-template-install
description: >
  Prepare or repair a macOS or Windows workstation for the AI SDLC template by verifying
  authenticated access to git.epam.com and checking or installing Python, pipx, a
  template-compatible Copier version, Node.js/npx, and uvx. Use when a user needs prerequisites
  for copier copy/update or MCP tools, or when the copier-update skill delegates installation,
  connectivity, or version repair.
---

# AI SDLC Template Install

Prepare the workstation without expecting the user to know package managers or PATH configuration.
Check before installing, verify every changed tool, and stop only when installation cannot continue.

## Rules

- Support macOS and Windows only. Stop with a clear explanation on Linux or an unidentified OS.
- Install only missing or unsupported tools.
- Prefer Homebrew on macOS, winget on Windows, and pipx for Copier.
- Verify Git is available and the user has authenticated read access to the AI SDLC template on
  `git.epam.com`.
- Run Git access checks non-interactively. Use credentials already available through the user's
  configured credential helper or SSH agent, but never open a terminal, GUI, or IDE credential
  prompt during a check. If credentials are unavailable, let the check fail and report setup advice.
- Never install Copier globally with `pip`.
- Never install an unbounded Copier version. If `.github/tested-copier-versions.txt` exists, read
  its `min` and `max`; otherwise use `>=9.0.0,<=9.99.99`.
- Never ask the user to paste a personal access token or private SSH key into chat, put one in a
  command or repository URL, print one, or save one in a repository file.
- After each installation or repair, rerun the tool's version command.
- If PATH changes, refresh the current shell and tell the user that a terminal restart may still
  be necessary.
- Track whether this run installed Node.js/npx or uv/uvx. If either was installed, tell the user to
  fully quit and restart VS Code or Rider so its integrated terminal and agents inherit the updated
  PATH. Name only the tool or tools installed; do not give this advice when both were already present.
- If another skill invoked this one, report completion and return control to that skill so it can
  resume automatically.
- After successful completion, always include this exact next-step instruction followed by the
  matching transport example from section 8:
  `Now you're ready to run 'copier copy <template-repo> <your-local-path>' in the terminal`

## 1. Detect the operating system

On macOS or another POSIX shell, run `uname -s` and continue only when it returns `Darwin`.

On Windows PowerShell, inspect:

```powershell
$PSVersionTable.PSEdition
[System.Environment]::OSVersion.VersionString
```

## 2. Verify Git and access to git.epam.com

Check Git first:

```text
git --version
```

If Git is missing, install it and verify the result. On macOS, use:

```bash
brew install git
git --version
```

If Homebrew is also missing, install it with the Homebrew command in the next section before
installing Git. On Windows, use:

```powershell
winget install --id Git.Git -e --source winget
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
git --version
```

Test authenticated read access over both HTTPS/PAT and SSH.

These checks must use only credentials that are already configured. They must never ask the user
for a Git username, password, PAT, or SSH key passphrase. A missing or expired credential is an
authentication failure to report after both transports have been tested, not a reason to prompt.

### HTTPS/PAT on macOS

```bash
GCM_INTERACTIVE=0 \
GIT_TERMINAL_PROMPT=0 \
GIT_ASKPASS=/usr/bin/false \
SSH_ASKPASS=/usr/bin/false \
git -c credential.interactive=false ls-remote https://git.epam.com/adno-dib/adno-dib.git HEAD
```

### HTTPS/PAT on Windows

```powershell
$savedGitPromptEnvironment = @{
    GCM_INTERACTIVE = [Environment]::GetEnvironmentVariable("GCM_INTERACTIVE", "Process")
    GIT_TERMINAL_PROMPT = [Environment]::GetEnvironmentVariable("GIT_TERMINAL_PROMPT", "Process")
    GIT_ASKPASS = [Environment]::GetEnvironmentVariable("GIT_ASKPASS", "Process")
    SSH_ASKPASS = [Environment]::GetEnvironmentVariable("SSH_ASKPASS", "Process")
}
$noPromptAskPass = Join-Path ([IO.Path]::GetTempPath()) ("git-no-prompt-{0}.cmd" -f [guid]::NewGuid())
Set-Content -LiteralPath $noPromptAskPass -Value '@exit /b 1' -Encoding Ascii

try {
    $env:GCM_INTERACTIVE = "0"
    $env:GIT_TERMINAL_PROMPT = "0"
    $env:GIT_ASKPASS = $noPromptAskPass
    $env:SSH_ASKPASS = $noPromptAskPass
    git -c credential.interactive=false ls-remote https://git.epam.com/adno-dib/adno-dib.git HEAD
    $httpsAccessExitCode = $LASTEXITCODE
} finally {
    foreach ($name in $savedGitPromptEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedGitPromptEnvironment[$name], "Process")
    }
    Remove-Item -LiteralPath $noPromptAskPass -Force -ErrorAction SilentlyContinue
}
```

Use `$httpsAccessExitCode` when classifying the HTTPS/PAT result. Do not rerun the command without
the non-interactive controls when it fails.

### SSH on macOS

```bash
GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=yes" git ls-remote git@git.epam.com:adno-dib/adno-dib.git HEAD
```

### SSH on Windows

```powershell
$env:GIT_SSH_COMMAND = "ssh -o BatchMode=yes -o StrictHostKeyChecking=yes"
git ls-remote git@git.epam.com:adno-dib/adno-dib.git HEAD
Remove-Item Env:GIT_SSH_COMMAND -ErrorAction SilentlyContinue
```

A returned `HEAD` hash from either check means access passed. Only report a connection failure after
both checks fail. Handle that combined failure according to its cause:

- For DNS resolution, timeout, proxy, TLS, connection-refused, or other transport errors, explain
  that this is a network/VPN or corporate certificate problem. Ask the user to connect to EPAM's
  network or VPN, then rerun the check. Also give this exact advice:
  `You might need to disable Zscaler.`
- For any authentication or authorization failure, give this concise advice:
  `Set up access to git.epam.com using HTTPS with a PAT or SSH with an SSH key, then rerun the check.`

Do not continue until at least one check returns the remote `HEAD` hash.

## 3. Ensure Python 3.8+

### macOS

```bash
python3 --version
```

If missing or too old, install Homebrew when necessary and then Python:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
python3 --version
```

Run the Homebrew installer only when `brew --version` fails.

### Windows

```powershell
python --version
```

If missing or too old:

```powershell
winget install --id Python.Python.3 --source winget
python --version
```

If `python` remains unavailable, try `py -3 --version`. If both commands fail after installation,
ask the user to restart the terminal, then resume verification.

## 4. Ensure pipx

### macOS

```bash
pipx --version
brew install pipx
pipx ensurepath
export PATH="$HOME/.local/bin:$PATH"
pipx --version
```

Run the installation commands only when the initial check fails. If necessary, verify with
`python3 -m pipx --version`.

### Windows

```powershell
pipx --version
python -m pip install --user pipx
python -m pipx ensurepath
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
pipx --version
```

If only `py -3` works, use it instead of `python` for the two module commands.

## 5. Ensure a compatible Copier version

Read the supported range from `.github/tested-copier-versions.txt` when present. Check:

```text
copier --version
```

If Copier is missing or outside the supported range, install or repair it with the supported
constraint. With the current contract, use:

### macOS

```bash
pipx install --force "copier>=9.0.0,<=9.99.99"
copier --version
```

If pipx is not yet on PATH, use `python3 -m pipx install --force` with the same package constraint.

### Windows

```powershell
pipx install --force "copier>=9.0.0,<=9.99.99"
copier --version
```

If pipx is not yet on PATH, use `python -m pipx install --force` with the same package constraint.

Verify that the reported version is within both the minimum and maximum. Do not continue merely
because the command exists.

## 6. Ensure Node.js and npx

Check both `node --version` and `npx --version`.

On macOS, if either is missing:

```bash
brew install node
node --version
npx --version
```

On Windows, if either is missing:

```powershell
winget install --id OpenJS.NodeJS.LTS --source winget
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
node --version
npx --version
```

## 7. Ensure uvx

Check `uvx --version`.

On macOS, install with `brew install uv`. If Homebrew cannot provide it, use Astral's installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uvx --version
```

On Windows:

```powershell
winget install --id astral-sh.uv --source winget
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
uvx --version
```

If winget cannot install uv, use Astral's documented PowerShell installer and then refresh PATH.

## 8. Verify and hand back

Rerun every version and access check and report a table with Check, Status, and Version or Result.
Completion requires:

- Git and authenticated read access to `adno-dib/adno-dib` over HTTPS/PAT or SSH
- Python 3.8+
- pipx
- Copier inside the repository's supported range
- Node.js and npx
- uvx

If this skill was invoked by `copier-update`, finish with: `Prerequisites are ready; resume the
copier-update preflight.` Do not ask the user to invoke the updater again.

If this run installed npx, uvx, or both, include the IDE restart advice from the Rules in the final
handoff after successful version verification. A terminal restart alone is not sufficient.

After successful completion, include this exact instruction:
`Now you're ready to run 'copier copy <template-repo> <your-local-path>' in the terminal`

Immediately after it, show the example for each access check that passed. The destination must be
the existing project path `./`:

- HTTPS/PAT: `copier copy https://git.epam.com/adno-dib/adno-dib.git ./`
- SSH: `copier copy git@git.epam.com:adno-dib/adno-dib.git ./`

If both access checks passed, show both labeled examples. If only one passed, show only that one.

If a command fails, report the failed command and its relevant output without claiming success.

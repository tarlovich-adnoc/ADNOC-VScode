#!/usr/bin/env bash
set -euo pipefail

# Verification gate for the 'dotnet' stack.
# Gates run fail-fast: deps -> format-check -> static-analysis -> test + coverage.

echo "==> [1/4] dotnet restore"
dotnet restore

echo "==> [2/4] format check (dotnet format --verify-no-changes)"
dotnet format --verify-no-changes

echo "==> [3/4] build (warnings as errors)"
dotnet build -warnaserror

echo "==> [4/4] test (with coverage)"
dotnet test --collect:"XPlat Code Coverage"

echo "All verification checks passed."

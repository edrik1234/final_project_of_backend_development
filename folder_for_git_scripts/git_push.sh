#!/bin/sh
set -e

# -----------------------------
# definition of environments:
# -----------------------------
# Windows PowerShell:
#   $env:GITHUB_TOKEN="your_token_here"
# Linux / Git Bash:
#   export GITHUB_TOKEN="your_token_here"
git config user.name "Edrian Netyosov" 2>/dev/null || git config --global user.name "Edrian Netyosov"
git config user.email "razer4832@gmail.com" 2>/dev/null || git config --global user.email "razer4832@gmail.com"

[ -z "$GITHUB_TOKEN" ] && { echo "Error: GITHUB_TOKEN is not set"; exit 1; }

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXPORT_FILE="$PROJECT_ROOT/data/game_sessions.json"
GIT_REPO_DIR="$PROJECT_ROOT/final_project_of_backend_development"
TARGET_FILE="$GIT_REPO_DIR/game_sessions.json"

REMOTE_USER="edrik1234"
REMOTE_REPO="final_project_of_backend_development"
BRANCH="main"

REMOTE="https://${GITHUB_TOKEN}@github.com/${REMOTE_USER}/${REMOTE_REPO}.git"

# -----------------------------
# checking files and folders
# -----------------------------
[ -f "$EXPORT_FILE" ] || { echo "Missing export file: $EXPORT_FILE"; exit 1; }
[ -d "$GIT_REPO_DIR/.git" ] || { echo "Git repo not found in $GIT_REPO_DIR"; exit 1; }

# -----------------------------
# only copying file
# -----------------------------
cp "$EXPORT_FILE" "$TARGET_FILE"

cd "$GIT_REPO_DIR"

# -----------------------------
# עדכון remote ל-HTTPS עם Token
# -----------------------------
git remote set-url origin "$REMOTE"

# -----------------------------
# git add + commit + push
# -----------------------------
git add game_sessions.json

if git diff --cached --quiet; then
  echo "No changes to push"
  exit 0
fi

git commit -m "Update game sessions $(TZ='Asia/Jerusalem' date +'%Y-%m-%d %H:%M:%S')"
git push origin "$BRANCH"
echo "JSON pushed successfully"

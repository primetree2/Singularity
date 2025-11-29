#!/usr/bin/env sh
set -e

echo "==> Code formatting script: Prettier + ESLint --fix"

# Ensure pnpm is available
if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is not installed. Install it: npm i -g pnpm"
  exit 1
fi

# Run Prettier across the repo
echo "Running Prettier --write on repository..."
pnpm -w -r exec -- prettier --write . || {
  echo "Prettier finished with errors (non-zero exit). Continuing..."
}

# Run ESLint --fix for TypeScript files
echo "Running ESLint --fix for .ts and .tsx files..."
# Try a focused set of paths; eslint will skip if not configured for some packages
pnpm -w -r exec -- eslint --ext .ts,.tsx --fix . || {
  echo "ESLint finished with errors (non-zero exit). Continuing..."
}

# Summary of changes (if repo is a git repo)
if command -v git >/dev/null 2>&1 && [ -d .git ]; then
  CHANGED_COUNT=$(git status --porcelain | wc -l)
  if [ "$CHANGED_COUNT" -gt 0 ]; then
    echo ""
    echo "Formatting made changes to $CHANGED_COUNT file(s):"
    git --no-pager status --porcelain
    echo ""
    echo "You can review and commit the changes:"
    echo "  git add -A && git commit -m \"chore: format code\""
  else
    echo ""
    echo "No formatting changes detected."
  fi
else
  echo ""
  echo "Not a git repository or git not available — unable to show summary of changed files."
fi

echo "Formatting complete."

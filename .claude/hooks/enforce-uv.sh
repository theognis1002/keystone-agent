#!/bin/bash
# Enforce uv usage — block bare pip, python, and pytest commands.
# All Python commands in this project must go through uv.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Nothing to check if there's no command
[ -z "$COMMAND" ] && exit 0

# Patterns that should be run through uv instead
# Match commands at the start of a line or after &&, ||, ;, |, or $()
# But exclude cases where "uv" already precedes them
if echo "$COMMAND" | grep -qE '(^|[;&|] *|^\(|`)(pip3?|python3?|pytest|mypy|ruff|black|isort|flake8|pyright) '; then
  # Check it's not already prefixed with uv
  if ! echo "$COMMAND" | grep -qE '(^|[;&|] *|^\(|`)uv (run|pip|tool run) '; then
    BARE_CMD=$(echo "$COMMAND" | grep -oE '(pip3?|python3?|pytest|mypy|ruff|black|isort|flake8|pyright)' | head -1)
    jq -n \
      --arg cmd "$BARE_CMD" \
      '{
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: ("Use uv instead of bare `" + $cmd + "`. Run `uv run " + $cmd + " ...` or `uv pip ...` instead. All Python tooling in this project must go through uv.")
        }
      }'
    exit 0
  fi
fi

exit 0

#!/bin/sh
set -eu

if [ "${HERMES_ENABLED:-false}" = "true" ]; then
  export HERMES_HOME="${HERMES_HOME:-/data/hermes}"
  mkdir -p "$HERMES_HOME"

  if [ -n "${LLM_API_KEY:-}" ] && [ -z "${OPENROUTER_API_KEY:-}" ]; then
    export OPENROUTER_API_KEY="$LLM_API_KEY"
  fi

  profile="${HERMES_PROFILE:-discord-bot}"
  if [ -n "$profile" ] && [ ! -d "$HERMES_HOME/profiles/$profile" ]; then
    hermes profile create "$profile" --clone >/tmp/hermes-profile-create.log 2>&1 \
      || hermes profile create "$profile" >>/tmp/hermes-profile-create.log 2>&1 \
      || true
  fi
fi

exec python -m bot.main

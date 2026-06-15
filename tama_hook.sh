#!/bin/bash
# Source this in ~/.bashrc:  source /home/martin/tama/tama_hook.sh

_TAMA="python3 /home/martin/tama/signal.py"
_TAMA_LAST_CMD=""
_TAMA_IDLE_THRESHOLD=1800   # 30 min without a command = sleep
_TAMA_LAST_ACTIVE=$(date +%s)
_TAMA_SLEEPING=0

_tama_preexec() {
    _TAMA_LAST_CMD="$BASH_COMMAND"
}
trap '_tama_preexec' DEBUG

_tama_postcmd() {
    local exit_code=$?
    local cmd="$_TAMA_LAST_CMD"
    local now=$(date +%s)

    # --- wake from sleep ---
    local idle=$(( now - _TAMA_LAST_ACTIVE ))
    if (( _TAMA_SLEEPING && idle < _TAMA_IDLE_THRESHOLD )); then
        $_TAMA wake &>/dev/null
        _TAMA_SLEEPING=0
    fi

    # --- idle → sleep ---
    if (( idle >= _TAMA_IDLE_THRESHOLD && !_TAMA_SLEEPING )); then
        $_TAMA sleep &>/dev/null
        _TAMA_SLEEPING=1
    fi

    _TAMA_LAST_ACTIVE=$now

    # --- route by command pattern ---
    case "$cmd" in
        # git commit already handled by post-commit hook; skip here
        git\ push*)
            # post-push hook handles it
            ;;
        git\ pull*|git\ fetch*|git\ merge*)
            # post-merge hook handles it
            ;;
        pip\ install*|pip3\ install*|uv\ add*|uv\ pip\ install*)
            $_TAMA feed pip &>/dev/null
            ;;
        cd\ *|pushd\ *|popd)
            $_TAMA feed explore &>/dev/null
            ;;
        python*\ *.py|python3*\ *.py|bash\ *.sh|sh\ *.sh|./*)
            if (( exit_code == 0 )); then
                $_TAMA feed script &>/dev/null
            else
                $_TAMA feed script_fail &>/dev/null
            fi
            ;;
        flake8*|black\ --check*|pylint*|ruff\ check*)
            if (( exit_code == 0 )); then
                $_TAMA lint pass &>/dev/null
            else
                $_TAMA lint_exit "$exit_code" &>/dev/null
            fi
            ;;
        make*|cargo\ build*|npm\ run*|go\ build*)
            if (( exit_code == 0 )); then
                $_TAMA feed build &>/dev/null
            fi
            ;;
        *)
            # general terminal activity — tiny pulse, don't spam
            $_TAMA feed activity &>/dev/null
            ;;
    esac
}

PROMPT_COMMAND="_tama_postcmd${PROMPT_COMMAND:+; $PROMPT_COMMAND}"

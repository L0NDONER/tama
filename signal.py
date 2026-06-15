#!/usr/bin/env python3
"""
CLI to send signals to the pet from external scripts/hooks.

Usage:
  signal.py feed <tier>       # feed by tier (see FEED_TIERS below)
  signal.py lint <path>       # run flake8 on path, apply result
  signal.py lint_exit <code>  # apply lint penalty from exit code
  signal.py tabs              # too-many-tabs penalty
  signal.py sleep             # pet goes idle (no terminal activity)
  signal.py wake              # pet wakes up
  signal.py vscode            # check if VS Code running, reward if so

Feed tiers:
  activity    tiny pulse for any shell command       (+1 / +1)
  explore     cd / directory change                  (+2 / +2)
  pip         pip install / uv add                   (+3 / +5)
  script      python/bash script ran successfully    (+3 / +4)
  script_fail script exited non-zero                 ( 0 / -3)
  build       make/cargo/npm build passed            (+4 / +6)
  commit      git commit                             (+6 / +10)
  pull        git pull/fetch                         (+5 / +8)
  push        git push                               (+8 / +12)
  deploy      EC2 / infra deploy                     (+15 / +20)
"""
import json
import os
import sys
import time
import subprocess

STATE_FILE = os.path.join(os.path.dirname(__file__), "pet_state.json")

FEED_TIERS = {
    "activity":    {"health":  1, "happiness":  1},
    "explore":     {"health":  2, "happiness":  2},
    "pip":         {"health":  3, "happiness":  5},
    "script":      {"health":  3, "happiness":  4},
    "script_fail": {"health":  0, "happiness": -3},
    "build":       {"health":  4, "happiness":  6},
    "commit":      {"health":  6, "happiness": 10},
    "pull":        {"health":  5, "happiness":  8},
    "push":        {"health":  8, "happiness": 12},
    "deploy":      {"health": 15, "happiness": 20},
}


def load():
    if not os.path.exists(STATE_FILE):
        return {"health": 80, "happiness": 80, "last_coding_time": time.time(), "sleeping": False}
    with open(STATE_FILE) as f:
        return json.load(f)


def save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def clamp(v):
    return max(0, min(100, v))


def cmd_feed(state, tier):
    if tier not in FEED_TIERS:
        print(f"Unknown tier '{tier}'. Valid: {', '.join(FEED_TIERS)}")
        sys.exit(1)
    t = FEED_TIERS[tier]
    state["health"] = clamp(state["health"] + t["health"])
    state["happiness"] = clamp(state["happiness"] + t["happiness"])
    if t["health"] > 0 or t["happiness"] > 0:
        state["last_coding_time"] = time.time()
        state["sleeping"] = False


def cmd_lint(state, path):
    try:
        result = subprocess.run(["flake8", path], capture_output=True, text=True)
        if result.returncode == 0:
            state["happiness"] = clamp(state["happiness"] + 8)
            state["health"] = clamp(state["health"] + 5)
            print("Lint passed! +8 happiness, +5 health.")
        else:
            issues = result.stdout.count("\n")
            penalty = min(20, issues * 2)
            state["happiness"] = clamp(state["happiness"] - penalty)
            print(f"Lint failed ({issues} issues). -{penalty} happiness.")
    except FileNotFoundError:
        print("flake8 not found: pip install flake8")
        sys.exit(1)


def cmd_lint_exit(state, code):
    if code == 0:
        state["happiness"] = clamp(state["happiness"] + 8)
        state["health"] = clamp(state["health"] + 5)
    else:
        state["happiness"] = clamp(state["happiness"] - 5)


def cmd_tabs(state):
    state["happiness"] = clamp(state["happiness"] - 15)
    state["health"] = clamp(state["health"] - 10)


def cmd_sleep(state):
    state["sleeping"] = True


def cmd_wake(state):
    state["sleeping"] = False
    state["last_coding_time"] = time.time()
    state["happiness"] = clamp(state["happiness"] + 3)


def cmd_vscode(state):
    try:
        import psutil
        names = {p.name().lower() for p in psutil.process_iter(["name"])}
        if any("code" in n for n in names):
            state["last_coding_time"] = time.time()
            state["happiness"] = clamp(state["happiness"] + 5)
    except ImportError:
        print("psutil not found: pip install psutil")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    state = load()
    cmd = sys.argv[1]

    if cmd == "feed":
        if len(sys.argv) < 3:
            print("Usage: signal.py feed <tier>")
            sys.exit(1)
        cmd_feed(state, sys.argv[2])
    elif cmd == "lint":
        if len(sys.argv) < 3:
            print("Usage: signal.py lint <path>")
            sys.exit(1)
        cmd_lint(state, sys.argv[2])
    elif cmd == "lint_exit":
        cmd_lint_exit(state, int(sys.argv[2]))
    elif cmd == "tabs":
        cmd_tabs(state)
    elif cmd == "sleep":
        cmd_sleep(state)
    elif cmd == "wake":
        cmd_wake(state)
    elif cmd == "vscode":
        cmd_vscode(state)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    save(state)


if __name__ == "__main__":
    main()

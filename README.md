# tama

A terminal-driven tamagotchi. Your coding habits keep it alive.

![happy](sprites/happy.png) ![okay](sprites/okay.png) ![sad](sprites/sad.png) ![dead](sprites/dead.png)

## How it works

The pet lives in a small always-on-top window and a system tray icon. It gains health and happiness from real terminal activity — git commits, pushes, deploys, pip installs, lint passes — and decays passively over time. Talking to Claude counts as thinking: no decay while the process is open.

## Install

```bash
git clone https://github.com/L0NDONER/tama
cd tama
pip install pillow pystray psutil
python3 pet.py
```

**Autostart on login:**
```bash
cp tama.desktop ~/.config/autostart/
```

## Metabolism

| Action | Health | Happiness |
|--------|--------|-----------|
| `git commit` | +6 | +10 |
| `git push` | +8 | +12 |
| EC2 deploy (`make sync`) | +15 | +20 |
| `git pull` / fetch | +5 | +8 |
| Lint pass | +5 | +8 |
| `pip install` / `uv add` | +3 | +5 |
| Script run (exit 0) | +3 | +4 |
| `make` / build pass | +4 | +6 |
| `cd` / directory change | +2 | +2 |
| Any shell command | +1 | +1 |
| Passive decay | −1/5min | −1/5min |
| 24h no coding | −2/5min | −3/5min |
| Too many tabs | −10 | −15 |
| Lint fail | 0 | −5 |
| Claude open | 0 | +1/5min |

## Wiring signals

**Shell metabolism** — add to `~/.bashrc`:
```bash
source /path/to/tama/tama_hook.sh
```

**Git hooks** — install in any repo:
```bash
cp tama/hooks/* /your/repo/.git/hooks/
```

Or globally (all repos):
```bash
git config --global core.hooksPath /path/to/tama/hooks
```

**Manual signals:**
```bash
python3 signal.py feed deploy    # feast after a deploy
python3 signal.py tabs           # too many tabs
python3 signal.py lint <path>    # run flake8, apply result
```

## States

| Sprite | Condition |
|--------|-----------|
| 😺 Happy | health > 70, happiness > 70 |
| 😼 Okay | health > 40, happiness > 40 |
| 😿 Sad | health > 20 |
| 💀 Dead | everything below 20 |

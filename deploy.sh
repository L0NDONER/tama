#!/bin/bash
# Wrap your real deploy command here, then feed the pet on success.
# Usage: ./deploy.sh [your normal deploy args...]

set -e

# --- put your actual deploy command below ---
# Examples:
#   ssh ec2-user@your-host 'cd /app && git pull && systemctl restart myapp'
#   ansible-playbook deploy.yml
#   eb deploy
# --------------------------------------------

echo "[deploy] Running deploy..."
# YOUR_DEPLOY_COMMAND "$@"

echo "[deploy] Done. Feeding the pet..."
python3 /home/martin/tama/signal.py feed deploy

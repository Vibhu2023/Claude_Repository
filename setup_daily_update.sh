#!/usr/bin/env bash
# Sets up a cron job to run pipeline_status.py every day at 10:00 AM.
# Usage: bash setup_daily_update.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(command -v python3)"
SCRIPT="${SCRIPT_DIR}/pipeline_status.py"
LOG="${SCRIPT_DIR}/reports/pipeline_cron.log"

if [[ ! -f "$SCRIPT" ]]; then
    echo "ERROR: $SCRIPT not found." >&2
    exit 1
fi

# Ensure reports/ directory exists so the log can be written
mkdir -p "${SCRIPT_DIR}/reports"

CRON_LINE="0 10 * * * $PYTHON $SCRIPT >> $LOG 2>&1"

# Add to crontab only if not already present
if crontab -l 2>/dev/null | grep -qF "$SCRIPT"; then
    echo "Cron job already installed:"
    crontab -l | grep "$SCRIPT"
else
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "Cron job installed:"
    echo "  $CRON_LINE"
fi

echo ""
echo "The pipeline status report will run every day at 10:00 AM."
echo "Output log: $LOG"
echo ""
echo "To run manually right now:"
echo "  $PYTHON $SCRIPT"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v '$SCRIPT' | crontab -"

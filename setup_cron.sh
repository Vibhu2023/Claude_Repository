#!/usr/bin/env bash
# Installs a cron job to run daily_status.py every day at 10:00 AM.
# Usage: bash setup_cron.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
CRON_ENTRY="0 10 * * * cd \"${SCRIPT_DIR}\" && ${PYTHON} daily_status.py --save >> \"${SCRIPT_DIR}/status_reports/cron.log\" 2>&1"

echo "Setting up daily 10 AM pipeline status cron job..."
echo "  Script : ${SCRIPT_DIR}/daily_status.py"
echo "  Python : ${PYTHON}"
echo "  Log    : ${SCRIPT_DIR}/status_reports/cron.log"
echo ""

# Add entry only if it doesn't already exist
(crontab -l 2>/dev/null | grep -v "daily_status.py"; echo "${CRON_ENTRY}") | crontab -

echo "Cron job installed. Current crontab:"
crontab -l | grep -E "daily_status|CRON"
echo ""
echo "Done. The report will run every day at 10:00 AM."
echo "Markdown reports are saved to: ${SCRIPT_DIR}/status_reports/"

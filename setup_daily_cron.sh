#!/bin/bash
# Sets up a daily 10 AM cron job to generate the hiring pipeline status report.
# Run once: bash setup_daily_cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(command -v python3)"
SCRIPT="$SCRIPT_DIR/daily_pipeline_update.py"
LOG_DIR="$SCRIPT_DIR/daily_reports"
CRON_JOB="0 10 * * * $PYTHON $SCRIPT --save >> $LOG_DIR/cron.log 2>&1"

mkdir -p "$LOG_DIR"

# Add to crontab if not already present
if crontab -l 2>/dev/null | grep -qF "$SCRIPT"; then
    echo "Cron job already exists. No changes made."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added:"
    echo "  $CRON_JOB"
fi

echo ""
echo "Daily reports will be saved to: $LOG_DIR/"
echo ""
echo "To run the report manually now:"
echo "  python3 $SCRIPT --save"
echo ""
echo "To view current crontab:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e   # then delete the pipeline_update line"

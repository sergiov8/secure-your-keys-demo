#!/usr/bin/env bash
# Lists active Security Command Center findings for the project, newest first.
# Requires Security Command Center to be activated for the project or its
# organization: https://cloud.google.com/security-command-center/docs/activate-scc-overview
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash bonus_security_command_center/list_findings.sh
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"

gcloud scc findings list \
  --project="${PROJECT}" \
  --filter='state="ACTIVE"' \
  --sort-by="~finding.eventTime" \
  --limit=20 \
  --format="table(finding.category, finding.severity, finding.eventTime, finding.resourceName)"

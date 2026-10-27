#!/usr/bin/env bash
# Lists Agent Platform quotas for the project so you can find the quota ID to
# lower with `gcloud quotas preferences create`. A lower ceiling limits how
# fast a bug, a runaway agent loop or a leaked credential can spend.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash bonus_spend_cap/list_quotas.sh
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"

gcloud quotas info list \
  --service=aiplatform.googleapis.com \
  --project="${PROJECT}" \
  --format="table(quotaId, metric, refreshInterval)" \
  --limit=50

#!/usr/bin/env bash
# Stores a third-party key in Secret Manager and lets only the runtime
# service account read it. The value is read from stdin so it never lands
# in your shell history.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash step3_secret_manager/store_secret.sh stripe-live-key
#   (paste the key, then press Ctrl-D)
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"
SECRET_ID="${1:?Usage: store_secret.sh SECRET_ID}"
SA_EMAIL="${SA_EMAIL:-agent-runtime@${PROJECT}.iam.gserviceaccount.com}"

gcloud services enable secretmanager.googleapis.com --project="${PROJECT}"

if gcloud secrets describe "${SECRET_ID}" --project="${PROJECT}" >/dev/null 2>&1; then
  # Existing secret: add a new version. Old versions stay until you disable them.
  gcloud secrets versions add "${SECRET_ID}" --project="${PROJECT}" --data-file=-
else
  gcloud secrets create "${SECRET_ID}" --project="${PROJECT}" --data-file=-
fi

# Grant access on this one secret, not on the whole project.
gcloud secrets add-iam-policy-binding "${SECRET_ID}" \
  --project="${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

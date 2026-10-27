#!/usr/bin/env bash
# Creates a runtime service account that can call Gemini models and nothing else,
# then shows how to attach it to a Cloud Run service.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash step2_least_privilege/setup_service_account.sh
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"
SA_NAME="${SA_NAME:-agent-runtime}"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"

gcloud services enable aiplatform.googleapis.com iam.googleapis.com --project="${PROJECT}"

if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --project="${PROJECT}" \
    --display-name="Runtime identity for the app"
fi

# roles/aiplatform.user lets the app call models. It cannot change IAM,
# delete resources or read your billing data.
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" \
  --condition=None

cat <<EOF

Done. Attach the identity when you deploy, for example:

  gcloud run deploy my-agent \\
    --image=us-docker.pkg.dev/${PROJECT}/agents/api:v1 \\
    --service-account=${SA_EMAIL} \\
    --region=us-central1

The code from step1_keyless_auth/after_keyless.py then runs with no key.
EOF

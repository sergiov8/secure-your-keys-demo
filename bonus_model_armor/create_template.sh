#!/usr/bin/env bash
# Creates a Model Armor template that screens for prompt injection and
# jailbreaks, malicious URLs and sensitive data.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash bonus_model_armor/create_template.sh
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
TEMPLATE_ID="${TEMPLATE_ID:-app-default}"

gcloud services enable modelarmor.googleapis.com --project="${PROJECT}"

gcloud model-armor templates create "${TEMPLATE_ID}" \
  --project="${PROJECT}" \
  --location="${LOCATION}" \
  --pi-and-jailbreak-filter-settings-enforcement=enabled \
  --pi-and-jailbreak-filter-settings-confidence-level=medium-and-above \
  --malicious-uri-filter-settings-enforcement=enabled \
  --basic-config-filter-enforcement=enabled

echo "Created projects/${PROJECT}/locations/${LOCATION}/templates/${TEMPLATE_ID}"

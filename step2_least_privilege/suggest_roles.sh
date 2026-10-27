#!/usr/bin/env bash
# Asks Gemini for the narrowest predefined roles for a task, using the
# Policy Assist API (Preview). This is the same engine behind
# "Help me choose roles" in the console.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash step2_least_privilege/suggest_roles.sh
#   bash step2_least_privilege/suggest_roles.sh "least privileged role to read one Cloud Storage bucket"
#
# Without words like "least privileged" or "narrowest access", the suggestions
# default to a service's broad Admin, Editor or Viewer roles.
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"
PROMPT="${1:-What is the narrowest access a service account needs to call Gemini models on Agent Platform?}"

gcloud services enable policyassist.googleapis.com --project="${PROJECT}"

python3 - "${PROMPT}" > /tmp/suggest_roles_request.json <<'PY'
import json, sys
print(json.dumps({"prompt": {"userInstructions": sys.argv[1]}}))
PY

curl -sS -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @/tmp/suggest_roles_request.json \
  "https://policyassist.googleapis.com/v1/projects/${PROJECT}/locations/global:recommendIamRoles"
echo

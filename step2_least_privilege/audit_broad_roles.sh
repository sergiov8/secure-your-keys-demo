#!/usr/bin/env bash
# Lists every service account that holds Owner or Editor on the project.
# A runtime identity with either role turns one leaked token into full control.
#
#   export GOOGLE_CLOUD_PROJECT=my-startup-prod
#   bash step2_least_privilege/audit_broad_roles.sh
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT first}"

gcloud projects get-iam-policy "${PROJECT}" \
  --flatten="bindings[].members" \
  --filter="bindings.role:(roles/owner OR roles/editor) AND bindings.members:serviceAccount" \
  --format="table(bindings.role, bindings.members)"

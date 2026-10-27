"""Creates a spend cap budget (Preview) that pauses one service in one project.

Unlike an alerts-only budget, a spend cap stops new requests once estimated
spend passes 100% of the amount. Alerts go to billing admins and project
owners at 50%, 80% and 100%.

    export GOOGLE_CLOUD_PROJECT=my-startup-prod
    python -m bonus_spend_cap.create_spend_cap --billing-account 012345-6789AB-CDEF01 --amount 500 --dry-run
    python -m bonus_spend_cap.create_spend_cap --billing-account 012345-6789AB-CDEF01 --amount 500

Needs billing.budgets.configureSpendCap, for example through the Billing
Account Administrator role. Each cap covers one project and one service, so
run it once per service you want to cap. Docs:
https://cloud.google.com/billing/docs/how-to/budget-api-spend-cap
"""

import argparse
import json
import sys

from common.config import ConfigError, load_settings

# Service IDs from the eligible services table in the spend cap docs.
ELIGIBLE_SERVICES = {
    "agent-platform": "C7E2-9256-1C43",  # aiplatform.googleapis.com
    "gemini-api": "AEFD-7695-64FA",  # generativelanguage.googleapis.com
    "cloud-run": "152E-C115-5142",  # run.googleapis.com
    "cloud-run-functions": "29E7-DA93-CA13",  # cloudfunctions.googleapis.com
}

BUDGETS_URL = "https://billingbudgets.googleapis.com/v1/billingAccounts/{account}/budgets"


def build_spend_cap_budget(project: str, service: str, amount_units: int) -> dict:
    """Returns a request body that satisfies the spend cap field restrictions."""
    if service not in ELIGIBLE_SERVICES:
        raise ValueError(
            f"{service!r} is not eligible. Choose one of: {', '.join(ELIGIBLE_SERVICES)}"
        )
    if amount_units <= 0:
        raise ValueError("amount must be a positive whole number")
    return {
        "displayName": f"{project} {service} spend cap",
        "budgetFilter": {
            "projects": [f"projects/{project}"],
            "services": [f"services/{ELIGIBLE_SERVICES[service]}"],
            # Spend caps are calculated on gross cost and must be monthly.
            "creditTypesTreatment": "EXCLUDE_ALL_CREDITS",
            "calendarPeriod": "MONTH",
        },
        "amount": {"specifiedAmount": {"units": str(amount_units)}},
        # Spend caps require exactly these three thresholds.
        "thresholdRules": [
            {"thresholdPercent": 0.5},
            {"thresholdPercent": 0.8},
            {"thresholdPercent": 1.0},
        ],
        "notificationsRule": {"enableProjectLevelRecipients": True},
        "spendCap": {"inputState": "CONFIGURED"},
    }


def create_budget(billing_account: str, quota_project: str, body: dict) -> dict:
    import google.auth
    from google.auth.transport.requests import AuthorizedSession

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-billing"]
    )
    session = AuthorizedSession(credentials)
    resp = session.post(
        BUDGETS_URL.format(account=billing_account),
        json=body,
        headers={"x-goog-user-project": quota_project},
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a spend cap budget.")
    parser.add_argument("--billing-account", required=True)
    parser.add_argument("--amount", type=int, required=True, help="Monthly cap in your billing currency")
    parser.add_argument("--service", default="agent-platform", choices=sorted(ELIGIBLE_SERVICES))
    parser.add_argument("--dry-run", action="store_true", help="Print the request body and exit")
    args = parser.parse_args()

    try:
        project = load_settings().project
    except ConfigError as e:
        sys.exit(str(e))
    body = build_spend_cap_budget(project, args.service, args.amount)
    if args.dry_run:
        print(json.dumps(body, indent=2))
        return
    created = create_budget(args.billing_account, project, body)
    print(f"Created {created['name']}")
    print("Enforcement uses estimated cost and is not instant. Set the cap below your real ceiling.")


if __name__ == "__main__":
    main()

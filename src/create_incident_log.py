from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REDACTED_FILE = (
    PROJECT_ROOT
    / "data/processed/support_tickets_redacted.csv"
)

EMAIL_PATTERN = (
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


# Validate the remediated dataset.
redacted = pd.read_csv(
    REDACTED_FILE,
    dtype="string",
)

comments = redacted["comment"].fillna("")

remaining_email_matches = int(
    comments.str.contains(
        EMAIL_PATTERN,
        regex=True,
    ).sum()
)

validation_passed = (
    remaining_email_matches == 0
)

if validation_passed:
    validation_result = (
        "PASS - automated scan found 0 remaining "
        "email patterns in remediated output"
    )
    incident_status = "CLOSED"
else:
    validation_result = (
        f"FAIL - automated scan found "
        f"{remaining_email_matches} remaining "
        f"email pattern(s)"
    )
    incident_status = "OPEN"


incident = {
    "incident_id": "PII-2026-001",
    "detected_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "dataset": "support_tickets",
    "pii_type": "Email address in free-text comment",
    "affected_records": 1,
    "severity": "HIGH",
    "detection_method": (
        "Automated regex scan followed by manual review"
    ),
    "containment_action": (
        "Affected output isolated and downstream use paused"
    ),
    "escalation_path": (
        "Data Owner -> Information Security -> Privacy"
    ),
    "root_cause": (
        "Free-text field allowed customer contact "
        "information without validation"
    ),
    "remediation": (
        "Email value redacted and automated PII "
        "validation added"
    ),
    "validation_result": validation_result,
    "status": incident_status,
}


incident_log = pd.DataFrame([incident])

output_path = (
    PROJECT_ROOT
    / "reports/pii_incident_log.csv"
)

incident_log.to_csv(
    output_path,
    index=False,
)


print("\nPII INCIDENT LOG")
print("=" * 80)

print(
    incident_log.to_string(
        index=False
    )
)

print("\nCONTROL CHECKS")
print("=" * 80)

print(
    f"Remaining email patterns: "
    f"{remaining_email_matches}"
)

if validation_passed:
    print(
        "PASS: Remediated output passed "
        "automated email exposure validation."
    )
else:
    print(
        "FAIL: Remediated output still contains "
        "possible email exposure."
    )

if (
    incident_status == "CLOSED"
    and validation_passed
):
    print(
        "PASS: Incident closure is supported "
        "by validation evidence."
    )
else:
    print(
        "BLOCKED: Incident remains open until "
        "validation passes."
    )

print(
    f"\nINCIDENT STATUS: {incident_status}"
)

print(
    "\nSaved: reports/pii_incident_log.csv"
)
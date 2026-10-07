from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SNAPSHOT_DATE = pd.Timestamp("2026-03-31")
RETENTION_DAYS = 365

tickets = pd.read_csv(
    PROJECT_ROOT / "data/processed/support_tickets_clean.csv",
    dtype="string",
)

tickets["created_at"] = pd.to_datetime(
    tickets["created_at"],
    errors="coerce",
)

tickets["age_days"] = (
    SNAPSHOT_DATE - tickets["created_at"]
).dt.days


def classify_retention(age_days):
    if pd.isna(age_days):
        return "REVIEW"

    if age_days > RETENTION_DAYS:
        return "ELIGIBLE_FOR_DELETION"

    return "KEEP"


tickets["retention_status"] = (
    tickets["age_days"]
    .apply(classify_retention)
)

tickets["retention_reason"] = tickets[
    "retention_status"
].map(
    {
        "KEEP": (
            "Within configured retention period"
        ),
        "ELIGIBLE_FOR_DELETION": (
            "Older than configured retention period; "
            "requires approval before deletion"
        ),
        "REVIEW": (
            "Missing or invalid date requires review"
        ),
    }
)


report_columns = [
    "ticket_id",
    "created_at",
    "age_days",
    "retention_status",
    "retention_reason",
]

report = tickets[report_columns].copy()

output_path = (
    PROJECT_ROOT
    / "reports/retention_review.csv"
)

report.to_csv(
    output_path,
    index=False,
)


print("\nRETENTION POLICY REVIEW")
print("=" * 75)

print(f"Snapshot date: {SNAPSHOT_DATE.date()}")
print(f"Configured retention period: {RETENTION_DAYS} days")
print(f"Total records reviewed: {len(report)}")

print("\nRETENTION STATUS")
print("=" * 75)

print(
    report["retention_status"]
    .value_counts()
    .to_string()
)

eligible = report[
    report["retention_status"]
    == "ELIGIBLE_FOR_DELETION"
]

review = report[
    report["retention_status"]
    == "REVIEW"
]

print(
    f"\nEligible for deletion review: "
    f"{len(eligible)}"
)

print(
    f"Manual review required: "
    f"{len(review)}"
)

print(
    "\nCONTROL: No records were deleted."
)

print(
    "Deletion requires policy approval and checks "
    "for legal hold, regulatory, contractual, "
    "or business retention requirements."
)

print(
    "\nSaved: reports/retention_review.csv"
)
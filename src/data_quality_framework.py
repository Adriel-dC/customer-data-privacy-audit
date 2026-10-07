from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

customers = pd.read_csv(
    PROJECT_ROOT / "data/processed/customers_clean.csv",
    dtype="string",
)

tickets = pd.read_csv(
    PROJECT_ROOT / "data/processed/support_tickets_clean.csv",
    dtype="string",
)

results = []


def add_result(
    check_name,
    dimension,
    metric,
    threshold,
    status,
    severity,
):
    results.append(
        {
            "check": check_name,
            "dimension": dimension,
            "metric": metric,
            "threshold": threshold,
            "status": status,
            "severity": severity,
        }
    )


# 1. UNIQUENESS
customer_uniqueness = (
    customers["customer_id"].nunique()
    / len(customers)
    * 100
)

add_result(
    "Customer ID uniqueness",
    "Uniqueness",
    f"{customer_uniqueness:.2f}%",
    "100%",
    "PASS" if customer_uniqueness == 100 else "FAIL",
    "CRITICAL",
)

ticket_uniqueness = (
    tickets["ticket_id"].nunique()
    / len(tickets)
    * 100
)

add_result(
    "Ticket ID uniqueness",
    "Uniqueness",
    f"{ticket_uniqueness:.2f}%",
    "100%",
    "PASS" if ticket_uniqueness == 100 else "FAIL",
    "CRITICAL",
)


# 2. COMPLETENESS
customer_id_completeness = (
    customers["customer_id"].notna().mean() * 100
)

add_result(
    "Customer ID completeness",
    "Completeness",
    f"{customer_id_completeness:.2f}%",
    "100%",
    "PASS" if customer_id_completeness == 100 else "FAIL",
    "CRITICAL",
)

ticket_customer_completeness = (
    tickets["customer_id"].notna().mean() * 100
)

add_result(
    "Ticket customer ID completeness",
    "Completeness",
    f"{ticket_customer_completeness:.2f}%",
    "100%",
    "PASS" if ticket_customer_completeness == 100 else "FAIL",
    "CRITICAL",
)


# 3. REFERENTIAL INTEGRITY
valid_customer_reference = (
    tickets["customer_id"]
    .isin(customers["customer_id"])
    .mean()
    * 100
)

if valid_customer_reference == 100:
    ref_status = "PASS"
elif valid_customer_reference >= 99:
    ref_status = "WARNING"
else:
    ref_status = "FAIL"

add_result(
    "Ticket to customer referential integrity",
    "Referential Integrity",
    f"{valid_customer_reference:.2f}%",
    ">=99%; target 100%",
    ref_status,
    "CRITICAL",
)


# 4. VALID DATES
parsed_dates = pd.to_datetime(
    tickets["created_at"],
    errors="coerce",
)

valid_date_rate = parsed_dates.notna().mean() * 100

add_result(
    "Valid ticket dates",
    "Validity",
    f"{valid_date_rate:.2f}%",
    "100%",
    "PASS" if valid_date_rate == 100 else "FAIL",
    "CRITICAL",
)


# 5. FRESHNESS
#
# A fixed snapshot date keeps the portfolio result reproducible.
# These thresholds are demonstration criteria for this project,
# not universal business or regulatory standards.

SNAPSHOT_DATE = pd.Timestamp("2026-03-31")

latest_ticket_date = parsed_dates.max()

if pd.isna(latest_ticket_date):
    freshness_days = None
    freshness_status = "FAIL"
    freshness_metric = "No valid date"

else:
    freshness_days = (
        SNAPSHOT_DATE - latest_ticket_date
    ).days

    freshness_metric = (
        f"{freshness_days} days"
    )

    if freshness_days <= 30:
        freshness_status = "PASS"

    elif freshness_days <= 60:
        freshness_status = "WARNING"

    else:
        freshness_status = "FAIL"


add_result(
    "Support ticket data freshness",
    "Freshness",
    freshness_metric,
    "PASS <=30d; WARNING 31-60d; FAIL >60d",
    freshness_status,
    "CRITICAL",
)


# 6. PII EXPOSURE
email_pattern = (
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

comments = tickets["comment"].fillna("")

email_exposure_count = (
    comments.str.contains(
        email_pattern,
        regex=True,
    ).sum()
)

add_result(
    "Unexpected email exposure in comments",
    "Privacy",
    int(email_exposure_count),
    "0",
    "PASS" if email_exposure_count == 0 else "FAIL",
    "CRITICAL",
)


# CREATE QA REPORT
report = pd.DataFrame(results)

report_path = (
    PROJECT_ROOT
    / "reports/data_quality_framework.csv"
)

report.to_csv(
    report_path,
    index=False,
)


print("\nDATA QUALITY REPORT")
print("=" * 80)

print(
    report.to_string(index=False)
)


print("\nSUMMARY")
print("=" * 80)

print(
    report["status"]
    .value_counts()
    .to_string()
)


critical_failures = report[
    (report["status"] == "FAIL")
    & (report["severity"] == "CRITICAL")
]

warnings = report[
    report["status"] == "WARNING"
]


if len(critical_failures) > 0:
    print(
        "\nPIPELINE STATUS: BLOCKED"
    )

    print(
        f"Critical failures: "
        f"{len(critical_failures)}"
    )

elif len(warnings) > 0:
    print(
        "\nPIPELINE STATUS: APPROVED WITH WARNINGS"
    )

    print(
        f"Warnings: {len(warnings)}"
    )

else:
    print(
        "\nPIPELINE STATUS: APPROVED"
    )


print(
    "\nSaved: reports/data_quality_framework.csv"
)
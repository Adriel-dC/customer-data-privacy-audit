from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
checks = []


def read_csv(relative_path, separator=","):
    return pd.read_csv(
        PROJECT_ROOT / relative_path,
        sep=separator,
        dtype="string",
    )


def check(description, condition):
    if not bool(condition):
        raise ValueError(f"FAIL: {description}")
    checks.append({"check": description, "result": "PASS"})
    print(f"PASS: {description}")


def same_records(left, right, columns, key):
    left = left[columns].sort_values(key).reset_index(drop=True)
    right = right[columns].sort_values(key).reset_index(drop=True)
    return left.equals(right)


raw_customers = read_csv("data/raw/customers.csv")
raw_tickets = read_csv("data/raw/support_tickets.csv")
redacted = read_csv("data/processed/support_tickets_redacted.csv")
customers = read_csv("data/processed/customers_clean.csv")
customer_review = read_csv("data/processed/customers_for_review.csv")
tickets = read_csv("data/processed/support_tickets_clean.csv")
ticket_review = read_csv("data/processed/support_tickets_for_review.csv")
labels = read_csv("reports/manual_review_labeled.csv", separator=";")

# Check row accounting and preservation of records.
check(
    "Customer row accounting",
    len(raw_customers)
    == len(customers) + len(customer_review)
    + int(raw_customers.duplicated().sum()),
)
check(
    "Ticket row accounting",
    len(redacted)
    == len(tickets) + len(ticket_review)
    + int(redacted.duplicated().sum()),
)
check(
    "Customer records preserved across accepted and review outputs",
    same_records(
        pd.concat([customers, customer_review]),
        raw_customers.drop_duplicates(),
        list(raw_customers.columns),
        list(raw_customers.columns),
    ),
)
check(
    "Ticket records preserved across accepted and review outputs",
    same_records(
        pd.concat([tickets, ticket_review]),
        redacted.drop_duplicates(),
        list(redacted.columns),
        list(redacted.columns),
    ),
)

check("Accepted customer IDs are unique", customers["customer_id"].is_unique)
check("Accepted ticket IDs are unique", tickets["ticket_id"].is_unique)
check(
    "Accepted tickets reference accepted customers",
    tickets["customer_id"].isin(customers["customer_id"]).all(),
)

dates = pd.to_datetime(
    tickets["created_at"],
    format="%Y-%m-%dT%H:%M:%S",
    errors="coerce",
)
check("Accepted ticket dates are valid", dates.notna().all())

# Compare redacted output with raw input, preserving row order.
check("Redaction preserves row count", len(raw_tickets) == len(redacted))
metadata_columns = ["ticket_id", "customer_id", "created_at", "category"]
check(
    "Redaction preserves ticket metadata",
    raw_tickets[metadata_columns].equals(redacted[metadata_columns]),
)
check(
    "Redaction preserves missing comments",
    raw_tickets["comment"].isna().equals(redacted["comment"].isna()),
)

email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
phone_pattern = (
    r"(?<!\w)(?:\+1[\s.-]?)?"
    r"(?:\(\d{3}\)|\d{3})[\s.-]?"
    r"\d{3}[\s.-]?\d{4}(?!\w)"
)
comments = redacted["comment"].fillna("")
check(
    "No email pattern matches remain in redacted comments",
    ~comments.str.contains(email_pattern, regex=True).any(),
)

# Every remaining phone candidate must have a matching review rejection.
for column in ["detected_phone", "actual_phone"]:
    values = labels[column].str.strip().str.lower()
    check(
        f"Valid review labels: {column}",
        values.isin(["true", "false"]).all(),
    )
    labels[column] = values.eq("true")

rejected = labels[
    labels["detected_phone"] & ~labels["actual_phone"]
]
approved_exceptions = set(zip(rejected["ticket_id"], rejected["comment"]))

remaining = redacted.loc[
    comments.str.contains(phone_pattern, regex=True)
]
check(
    "Remaining phone candidates match reviewed exceptions",
    all(
        (row["ticket_id"], row["comment"]) in approved_exceptions
        for _, row in remaining.iterrows()
    ),
)

email_missing = customers["email"].isna()
email_invalid = (
    customers["email"].notna()
    & ~customers["email"].str.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", na=False
    )
)

flag_checks = [
    (customers, "email_missing", email_missing),
    (customers, "email_invalid", email_invalid),
    (tickets, "comment_missing", tickets["comment"].isna()),
]

for dataframe, column, expected in flag_checks:
    saved = dataframe[column].str.strip().str.lower()

    check(
        f"Valid saved flags: {column}",
        saved.isin(["true", "false"]).all(),
    )
    check(
        f"Saved flags match data: {column}",
        saved.eq("true").astype("bool").equals(
            expected.astype("bool")
        ),
    )

pd.DataFrame(checks).to_csv(
    PROJECT_ROOT / "reports/output_validation.csv",
    index=False,
)
print(f"\nAll {len(checks)} checks passed.")
print("Saved: reports/output_validation.csv")
print("Pattern checks do not establish complete PII removal.")


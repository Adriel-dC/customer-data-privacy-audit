from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

customers = pd.read_csv(
    PROJECT_ROOT / "data/raw/customers.csv",
    dtype="string",
)
tickets = pd.read_csv(
    OUTPUT_DIR / "support_tickets_redacted.csv",
    dtype="string",
)

customer_duplicates = int(customers.duplicated().sum())
ticket_duplicates = int(tickets.duplicated().sum())

customers = customers.drop_duplicates().copy()
tickets = tickets.drop_duplicates().copy()

# Quarantine every version of a conflicting customer record.
conflicting_records = customers["customer_id"].duplicated(keep=False)
conflicting_ids = customers.loc[
    conflicting_records, "customer_id"
]

customer_review = customers.loc[conflicting_records].copy()
customer_review["review_reason"] = "Conflicting customer records"

clean_customers = customers.loc[~conflicting_records].copy()

# Preserve email values and flag their limitations.
email_pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
clean_customers["email_missing"] = clean_customers["email"].isna()
clean_customers["email_invalid"] = (
    clean_customers["email"].notna()
    & ~clean_customers["email"].str.fullmatch(
        email_pattern, na=False
    )
)

# Distinguish unknown customers from unresolved customer conflicts.
parsed_dates = pd.to_datetime(
    tickets["created_at"],
    format="%Y-%m-%dT%H:%M:%S",
    errors="coerce",
)

tickets["date_invalid_or_missing"] = parsed_dates.isna()
tickets["customer_unknown"] = ~tickets["customer_id"].isin(
    customers["customer_id"]
)
tickets["customer_conflicting"] = tickets["customer_id"].isin(
    conflicting_ids
)
tickets["comment_missing"] = tickets["comment"].isna()

review_flags = [
    "date_invalid_or_missing",
    "customer_unknown",
    "customer_conflicting",
]
needs_review = tickets[review_flags].any(axis=1)

ticket_review = tickets.loc[needs_review].copy()
ticket_review["review_reason"] = ticket_review[review_flags].apply(
    lambda row: "; ".join(
        flag for flag in review_flags if row[flag]
    ),
    axis=1,
)

clean_tickets = tickets.loc[~needs_review].copy()

# Check the relationship between the accepted tables.
assert clean_customers["customer_id"].is_unique
assert clean_tickets["ticket_id"].is_unique
assert clean_tickets["customer_id"].isin(
    clean_customers["customer_id"]
).all()

outputs = {
    "customers_clean.csv": clean_customers,
    "customers_for_review.csv": customer_review,
    "support_tickets_clean.csv": clean_tickets,
    "support_tickets_for_review.csv": ticket_review,
}

for filename, dataframe in outputs.items():
    dataframe.to_csv(OUTPUT_DIR / filename, index=False)

summary = {
    "customer_duplicates_removed": customer_duplicates,
    "ticket_duplicates_removed": ticket_duplicates,
    "conflicting_customer_ids": conflicting_ids.nunique(),
    "customer_rows_for_review": len(customer_review),
    "accepted_customer_rows": len(clean_customers),
    "ticket_rows_for_review": len(ticket_review),
    "accepted_ticket_rows": len(clean_tickets),
    "accepted_customers_missing_email": int(
        clean_customers["email_missing"].sum()
    ),
    "accepted_customers_invalid_email": int(
        clean_customers["email_invalid"].sum()
    ),
}

pd.DataFrame(
    summary.items(), columns=["check", "count"]
).to_csv(
    PROJECT_ROOT / "reports/cleaning_summary.csv",
    index=False,
)

print("--- Cleaning summary ---")
for check, count in summary.items():
    print(f"{check}: {count}")

print("\nProcessed files and cleaning summary saved.")
print("Missing comments retained and flagged.")
print("Customer names and emails remain in customer outputs.")
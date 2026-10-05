from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

customers = pd.read_csv(
    PROJECT_ROOT / "data/raw/customers.csv",
    dtype="string",
)

tickets = pd.read_csv(
    PROJECT_ROOT / "data/raw/support_tickets.csv",
    dtype="string",
)

for name, dataset in [("Customers", customers), ("Support tickets", tickets)]:
    print(f"\n--- {name} ---")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")

    print("\nMissing values:")
    print(dataset.isna().sum())

    print(f"\nExact duplicate rows: {dataset.duplicated().sum()}")

# Check email format without counting missing emails twice.
email_pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"

invalid_emails = (
    customers["email"].notna()
    & ~customers["email"].str.fullmatch(email_pattern, na=False)
)

# Parse timestamps using the expected input format.
parsed_dates = pd.to_datetime(
    tickets["created_at"],
    format="%Y-%m-%dT%H:%M:%S",
    errors="coerce",
)

invalid_dates = tickets["created_at"].notna() & parsed_dates.isna()

# Check whether each ticket references an existing customer.
unknown_customers = (
    tickets["customer_id"].notna()
    & ~tickets["customer_id"].isin(customers["customer_id"])
)

# Separate conflicting records from exact duplicates.
unique_customer_rows = customers.drop_duplicates()
conflict_counts = unique_customer_rows.groupby("customer_id").size()
conflicting_ids = conflict_counts[conflict_counts > 1].index

print("\n--- Additional quality checks ---")
print(f"Invalid email formats: {invalid_emails.sum()}")
print(f"Invalid ticket dates: {invalid_dates.sum()}")
print(f"Tickets with unknown customers: {unknown_customers.sum()}")
print(f"Customer IDs with conflicting records: {len(conflicting_ids)}")

# Detect potential contact details in free-text comments.
EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

PHONE_PATTERN = (
    r"(?<!\w)(?:\+1[\s.-]?)?"
    r"(?:\(\d{3}\)|\d{3})[\s.-]?"
    r"\d{3}[\s.-]?\d{4}(?!\w)"
)

comments = tickets["comment"].fillna("")

email_flags = comments.str.contains(EMAIL_PATTERN, regex=True)
phone_flags = comments.str.contains(PHONE_PATTERN, regex=True)
contact_flags = email_flags | phone_flags

print("\n--- Potential PII in comments ---")
print(f"Comments with email matches: {email_flags.sum()}")
print(f"Comments with phone matches: {phone_flags.sum()}")
print(f"Comments with either match: {contact_flags.sum()}")

# Inspect the invoice example for a possible false positive.
invoice_example = tickets.loc[
    comments.str.contains("invoice 1234567890", regex=False),
    ["ticket_id", "comment"],
].copy()

invoice_example["phone_flag"] = phone_flags.loc[invoice_example.index]

print("\n--- Invoice example review ---")
print(invoice_example.to_string(index=False))

# Build a small sample for manual review.
invoice_indices = invoice_example.index

flagged_sample = tickets.loc[
    contact_flags & ~tickets.index.isin(invoice_indices)
].sample(n=10, random_state=42)

unflagged_sample = tickets.loc[
    ~contact_flags & tickets["comment"].notna()
].sample(n=9, random_state=42)

review_sample = pd.concat([
    flagged_sample,
    unflagged_sample,
    tickets.loc[invoice_indices],
]).sample(frac=1, random_state=42)

review_sample = review_sample[["ticket_id", "comment"]].copy()
review_sample["detected_email"] = email_flags.loc[review_sample.index]
review_sample["detected_phone"] = phone_flags.loc[review_sample.index]

# These fields must be completed by the reviewer.
review_sample["actual_email"] = ""
review_sample["actual_phone"] = ""
review_sample["review_notes"] = ""

review_sample.to_csv(
    PROJECT_ROOT / "reports/manual_review.csv",
    index=False,
)

print("\nManual review sample saved: 20 comments.")
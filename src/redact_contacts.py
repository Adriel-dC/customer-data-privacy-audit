from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
PHONE_PATTERN = (
    r"(?<!\w)(?:\+1[\s.-]?)?"
    r"(?:\(\d{3}\)|\d{3})[\s.-]?"
    r"\d{3}[\s.-]?\d{4}(?!\w)"
)

tickets = pd.read_csv(
    PROJECT_ROOT / "data/raw/support_tickets.csv",
    dtype="string",
)

review = pd.read_csv(
    PROJECT_ROOT / "reports/manual_review_labeled.csv",
    sep=";",
    dtype="string",
)

# Only exempt phone matches explicitly rejected during review.
for column in ["detected_phone", "actual_phone"]:
    labels = review[column].str.strip().str.lower()
    if not labels.isin(["true", "false"]).all():
        raise ValueError(f"Missing or invalid labels in {column}")
    review[column] = labels.eq("true")

rejected_matches = review[
    review["detected_phone"] & ~review["actual_phone"]
]

# Match both ticket ID and comment so changed text needs a new review.
phone_exemptions = set(
    zip(rejected_matches["ticket_id"], rejected_matches["comment"])
)

processed = tickets.copy()
email_count = 0
phone_count = 0
changed_comments = 0
preserved_candidates = 0

for index, row in tickets.iterrows():
    comment = row["comment"]

    if pd.isna(comment):
        continue

    redacted, emails = re.subn(
        EMAIL_PATTERN, "[EMAIL]", comment
    )

    if (row["ticket_id"], comment) in phone_exemptions:
        phones = 0
        preserved_candidates += len(
            re.findall(PHONE_PATTERN, redacted)
        )
    else:
        redacted, phones = re.subn(
            PHONE_PATTERN, "[PHONE]", redacted
        )

    processed.at[index, "comment"] = redacted
    email_count += emails
    phone_count += phones
    changed_comments += int(redacted != comment)

output_path = (
    PROJECT_ROOT / "data/processed/support_tickets_redacted.csv"
)
output_path.parent.mkdir(parents=True, exist_ok=True)
processed.to_csv(output_path, index=False)

print(f"Output rows: {len(processed)}")
print(f"Email matches replaced: {email_count}")
print(f"Phone matches replaced: {phone_count}")
print(f"Comments changed: {changed_comments}")
print(f"Reviewed phone candidates preserved: {preserved_candidates}")
print(f"Missing comments preserved: {processed['comment'].isna().sum()}")
print("Saved: data/processed/support_tickets_redacted.csv")
print("Scope: email and phone redaction only; other PII may remain.")
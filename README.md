# Customer Data Quality & Privacy Audit

A Python portfolio project that audits synthetic customer and support
data, identifies quality issues, and redacts email and phone matches
from support comments.

## Business scenario

Customer support exports can contain duplicate records, invalid values,
broken customer references, and contact details in free-text comments.

This project simulates reviewing those exports before downstream
analysis. Records with unresolved issues are separated for review,
while missing values are retained and flagged.

All data is synthetic. This is a personal project, not client work.

## Results

| Outcome | Customers | Support tickets |
| --- | ---: | ---: |
| Input rows | 505 | 1,003 |
| Exact duplicates removed | 3 | 3 |
| Records separated for review | 4 | 18 |
| Accepted records | 498 | 982 |

The redaction step runs before quality filtering and replaces:

- 40 email matches.
- 30 phone matches.
- Contact details in 60 comments.

One reviewed invoice number is preserved because it was incorrectly
flagged as a phone number.

All 21 output validation checks passed.

## Key decisions

- Separate conflicting customer records instead of choosing a version
  without supporting evidence.
- Separate tickets with invalid dates or unresolved customer references.
- Preserve missing comments and flag them.
- Retain missing and invalid customer emails with quality flags.
- Apply the reviewed phone exception only when the ticket ID and
  original comment both match.

Accepted customer records still contain eight missing emails and five
invalid email formats. These need correction before email outreach.

## Detection review

A targeted sample of 20 comments was labeled with AI assistance.

| Detector | True positives | False positives | False negatives | True negatives |
| --- | ---: | ---: | ---: | ---: |
| Email | 5 | 0 | 0 | 15 |
| Phone | 5 | 1 | 0 | 14 |

The phone false positive was an invoice number.

These results describe the reviewed sample only. They are not an
independent human benchmark or an estimate of full-dataset performance.

## Project structure

- `src/`: generation, auditing, evaluation, redaction, cleaning,
  and validation scripts.
- `data/raw/`: synthetic input datasets.
- `data/processed/`: redacted, accepted, and review datasets.
- `reports/`: review labels, metrics, quality summaries,
  validation results, and written findings.

## Running the workflow

Requirements: Python and pandas.

Run the following commands from the project root:

```powershell
python src/generate_dataset.py
python src/audit_data.py
```

Before evaluation, the review sample must be labeled and saved as
`reports/manual_review_labeled.csv`. This project includes the
AI-assisted labels used for the documented review.

Then run:

```powershell
python src/evaluate_detection.py
python src/redact_contacts.py
python src/clean_data.py
python src/validate_outputs.py
```

The labeled review file uses semicolon delimiters. Other CSV outputs
use comma delimiters.

## Reports

- [Data quality report](reports/data_quality_report.md)
- [Detection review](reports/detection_review.md)
- [Detection metrics](reports/detection_metrics.csv)
- [Detection disagreements](reports/detection_disagreements.csv)
- [Cleaning summary](reports/cleaning_summary.csv)
- [Output validation](reports/output_validation.csv)

## Limitations

Email and phone detection uses regular expressions and can produce
false positives or miss other formats.

Redaction covers email and phone matches in support comments only.
Other personal information may remain, and customer outputs retain
names and email values.

Passing the validation checks does not establish complete removal
of personal information.

## Tools

Python, pandas, regular expressions, and CSV-based review.
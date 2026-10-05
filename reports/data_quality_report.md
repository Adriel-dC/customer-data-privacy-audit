# Data Quality Report

## Project scope
Personal portfolio project using synthetic customer and support data.
The workflow checks data quality and redacts email and phone matches
in support comments.

## Initial findings
| Check | Customers | Support tickets |
| --- | ---: | ---: |
| Input rows | 505 | 1,003 |
| Exact duplicate rows | 3 | 3 |
| Missing emails | 8 | — |
| Invalid email formats | 5 | — |
| Missing comments | — | 6 |
| Invalid ticket dates | — | 4 |
| Tickets referencing unknown customers | — | 10 |
| Customer IDs with conflicting records | 2 | — |

Issue counts may overlap and should not be added together.

## Treatment decisions
- Removed exact duplicate rows.
- Separated all four records belonging to two conflicting customer IDs.
- Separated tickets with invalid dates, unknown customers, or references
  to conflicting customer IDs.
- Retained missing comments and added a flag.
- Retained missing and invalid customer emails with separate flags.
- Did not invent replacement values or choose an unsupported version
  of a conflicting customer record.

## Output reconciliation
| Dataset | Input rows | Duplicates removed | Rows for review | Accepted rows |
| --- | ---: | ---: | ---: | ---: |
| Customers | 505 | 3 | 4 | 498 |
| Support tickets | 1,003 | 3 | 18 | 982 |

Accepted customer records still include eight missing emails and five
invalid email formats. They require correction before email outreach.

## Contact redaction
Before quality filtering, the redaction step replaced 40 email matches
and 30 phone matches across 60 comments.

One reviewed invoice number was preserved as a rejected phone match.
The exception applies only when both the ticket ID and comment match
the reviewed record.

## Validation
All 21 output checks passed. Checks cover record reconciliation,
unique accepted IDs, customer references, ticket dates, preservation
of metadata and missing comments, saved flags, and remaining contact
pattern matches.

Detailed results: output_validation.csv.

## Limitations
Detection covers email and phone patterns only.
Pattern checks do not establish complete PII removal.
Customer outputs retain names and email values.
The 20-comment detection review used AI-assisted labels and a targeted
sample; its results do not represent the full dataset.

## Next actions
Resolve conflicting customer records using an authoritative source.
Correct invalid dates and investigate unknown customer references.
Request missing or corrected emails before contact-dependent use.
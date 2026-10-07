# Customer Data Quality & Privacy Audit

A Python portfolio project that simulates a production-style data quality and privacy review of synthetic customer and support datasets.

The project goes beyond basic data cleaning by implementing automated quality gates, join-cardinality controls, statistical and risk-based sampling, PII redaction validation, incident-response evidence, retention review, and a simulated Data Subject Access Request (DSAR) workflow.

All data is synthetic. This is a personal portfolio project, not client work.

---

## Business Scenario

Customer and support datasets can contain:

- Duplicate records
- Invalid or missing values
- Broken customer references
- Unexpected PII in free-text fields
- Join fanout caused by incorrect cardinality
- Stale data
- Records requiring manual review

The objective is to identify these risks before data reaches reporting or downstream analysis.

Instead of silently correcting every issue, the workflow separates uncertain records for review, validates accepted records, and blocks critical failures.

---

## Dataset

| Dataset | Input Rows | Accepted | Review | Exact Duplicates Removed |
| --- | ---: | ---: | ---: | ---: |
| Customers | 505 | 498 | 4 | 3 |
| Support tickets | 1,003 | 982 | 18 | 3 |

The processed support dataset contains four business categories:

| Category | Records |
| --- | ---: |
| Account | 267 |
| Subscription | 255 |
| Billing | 231 |
| Technical | 229 |

---

## Data Quality Framework

The automated QA framework validates multiple quality dimensions before approving the dataset.

Current checks include:

- Primary-key uniqueness
- Required-key completeness
- Referential integrity
- Date validity
- Data freshness
- Unexpected email exposure

Example acceptance rules:

| Quality Check | Threshold |
| --- | --- |
| Customer ID uniqueness | 100% |
| Ticket ID uniqueness | 100% |
| Required key completeness | 100% |
| Referential integrity | Target 100%; warning threshold >=99% |
| Valid ticket dates | 100% |
| Ticket freshness | PASS <=30 days; WARNING 31-60; FAIL >60 |
| Unexpected email exposure | 0 |

The current processed dataset passes all 8 framework checks.

**Pipeline status: APPROVED**

Freshness uses a fixed snapshot date so portfolio results remain reproducible. The thresholds are demonstration criteria and are not universal business or regulatory standards.

---

## Join Cardinality & Fanout Prevention

The customer-to-ticket relationship is expected to be:

`Customers (1) -> Support Tickets (N)`

Before joining, the workflow validates:

- Parent-key uniqueness
- Distinct-key counts
- Foreign-key integrity
- Expected relationship cardinality
- Row counts before and after the join

The pandas merge uses:

```python
validate="many_to_one"
```

Current validation:

```text
Customers: 498 rows / 498 unique customer IDs
Tickets:   982 rows / 428 unique customer IDs
Unmatched child keys: 0

Rows before join: 982
Rows after join:  982
Row delta:        0
```

A controlled test intentionally duplicates a customer key in memory.

The validator detects the duplicate before the join and blocks the operation, preventing silent fanout.

The project also documents when different solutions are appropriate:

- Deduplication for true data-quality duplicates
- Pre-aggregation when the analysis requires a higher grain
- Grain changes when detailed relationships are required
- Bridge tables for legitimate many-to-many business relationships

See [Join Cardinality Strategy](reports/join_cardinality_strategy.md).

---

## Statistical & Risk-Based Sampling

Manual review combines representative statistical sampling with targeted high-risk review.

For the 982 processed support tickets, the demonstration uses:

- 95% confidence level
- 5% margin of error
- 50% expected proportion
- Finite population correction

Calculated statistical sample:

**277 records**

The sample is proportionally stratified across business categories:

| Category | Population | Sample |
| --- | ---: | ---: |
| Account | 267 | 75 |
| Subscription | 255 | 72 |
| Billing | 231 | 65 |
| Technical | 229 | 65 |
| **Total** | **982** | **277** |

The pipeline separately searches for higher-risk records using existing quality flags.

Six high-risk records were identified, and none appeared in the random sample.

All six were therefore added through targeted risk-based selection.

**Final review set: 283 records**

This demonstrates why statistical sampling and targeted review are complementary rather than interchangeable.

See [Sampling Strategy](reports/sampling_strategy.md).

---

## PII Detection & Redaction

The redaction workflow runs before quality filtering.

It replaces detected contact information in support comments:

- 40 email matches
- 30 phone matches
- Contact information across 60 comments

A reviewed invoice number is preserved because it was incorrectly detected as a phone number.

A targeted sample of 20 comments was manually labeled with AI assistance:

| Detector | True Positives | False Positives | False Negatives | True Negatives |
| --- | ---: | ---: | ---: | ---: |
| Email | 5 | 0 | 0 | 15 |
| Phone | 5 | 1 | 0 | 14 |

These metrics describe the reviewed sample only. They are not an independent human benchmark or an estimate of full-dataset detector performance.

---

## Privacy Incident Workflow

The project includes a simulated PII incident-response process:

`Detect -> Contain -> Assess -> Escalate -> Remediate -> Validate -> Document`

The incident record captures:

- Incident ID
- Detection timestamp
- Dataset
- PII type
- Severity
- Containment action
- Escalation path
- Root cause
- Remediation
- Validation evidence
- Status

Incident closure is not based only on a manually entered status.

The remediated dataset is scanned again, and the simulated incident can close only when automated validation finds no remaining email pattern associated with the tested exposure.

Legal or regulatory notification decisions are outside the analyst workflow and would belong to the appropriate privacy, legal, security, or compliance teams.

See [PII Incident Workflow](reports/pii_incident_workflow.md).

---

## Retention Review

The project includes a reproducible retention-policy simulation.

Configuration:

```text
Snapshot date: 2026-03-31
Demonstration retention period: 365 days
```

Results:

| Status | Records |
| --- | ---: |
| KEEP | 883 |
| ELIGIBLE_FOR_DELETION | 99 |
| REVIEW | 0 |

No records are automatically deleted.

`ELIGIBLE_FOR_DELETION` means the record passed the configured age rule and should be reviewed against applicable policy, legal hold, regulatory, contractual, and business requirements before deletion.

The 365-day period is a demonstration policy, not a claim that GDPR, LGPD, or another regulation universally requires this retention period.

---

## DSAR Simulation

The project simulates a Data Subject Access Request across multiple datasets.

For the demonstration customer:

```text
Customer records found: 1
Related support tickets found: 7
Status: READY_FOR_REVIEW
```

The workflow:

1. Simulates identity verification.
2. Locates the customer record.
3. Finds related support records.
4. Creates an access package.
5. Creates an audit log.
6. Holds the package for authorized review.

Knowing a customer ID alone would not constitute sufficient identity verification in a real process.

Direct identifiers such as name and email are redacted from the public portfolio artifact.

`READY_FOR_REVIEW` does not mean the data was released to the requester.

---

## Key Data Decisions

The workflow intentionally avoids automatically "fixing" uncertain records.

Examples:

- Conflicting customer records are separated instead of arbitrarily choosing a version.
- Tickets with invalid dates or unresolved customer references are separated for review.
- Missing comments are retained and flagged.
- Missing and invalid customer emails remain visible through quality flags.
- Reviewed regex exceptions require both the ticket ID and original comment to match.
- Unexpected join cardinality blocks the operation instead of silently multiplying rows.
- Critical quality failures block pipeline approval.
- High-risk records are added to manual review even when random sampling misses them.
- Retention eligibility does not trigger automatic deletion.

---

## Project Structure

```text
customer-data-privacy-audit/
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- reports/
|   |-- data_quality_framework.csv
|   |-- join_cardinality_strategy.md
|   |-- sampling_strategy.md
|   |-- stratified_review_sample.csv
|   |-- combined_review_sample.csv
|   |-- pii_incident_workflow.md
|   |-- pii_incident_log.csv
|   |-- retention_review.csv
|   |-- dsar_access_package.csv
|   `-- dsar_request_log.csv
|
|-- src/
|   |-- generate_dataset.py
|   |-- audit_data.py
|   |-- evaluate_detection.py
|   |-- redact_contacts.py
|   |-- clean_data.py
|   |-- validate_outputs.py
|   |-- data_quality_framework.py
|   |-- validate_relationships.py
|   |-- sampling_strategy.py
|   |-- create_incident_log.py
|   |-- retention_policy.py
|   `-- dsar_request.py
|
|-- README.md
`-- requirements.txt
```

---

## Running the Workflow

Tested with Python 3.13 and pandas 3.0.6.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Run the core data workflow:

```powershell
python src/generate_dataset.py
python src/audit_data.py
python src/evaluate_detection.py
python src/redact_contacts.py
python src/clean_data.py
python src/validate_outputs.py
```

Then run the extended controls:

```powershell
python src/data_quality_framework.py
python src/validate_relationships.py
python src/sampling_strategy.py
python src/create_incident_log.py
python src/retention_policy.py
python src/dsar_request.py
```

Before detection evaluation, the review sample must be labeled and saved as `reports/manual_review_labeled.csv`.

The repository includes the AI-assisted labels used for the documented portfolio review.

---

## Key Reports

- [Data Quality Report](reports/data_quality_report.md)
- [Automated Quality Framework](reports/data_quality_framework.csv)
- [Output Validation](reports/output_validation.csv)
- [Detection Review](reports/detection_review.md)
- [Join Cardinality Strategy](reports/join_cardinality_strategy.md)
- [Sampling Strategy](reports/sampling_strategy.md)
- [PII Incident Workflow](reports/pii_incident_workflow.md)
- [Retention Review](reports/retention_review.csv)
- [DSAR Public Access Package](reports/dsar_access_package.csv)

---

## Limitations

This project uses synthetic data and simplified workflows for portfolio demonstration.

Email and phone detection relies on regular expressions. Regex detection can produce false positives and can miss formats or other types of personal information.

Redaction focuses on email and phone patterns in support comments. It does not establish complete PII discovery or removal across all fields.

Customer datasets intentionally retain synthetic names and email values because those fields are part of the simulated operational dataset.

The statistical sampling parameters are demonstration choices and should be adapted to business risk, review cost, regulatory requirements, and the consequences of missed errors.

The retention policy is simulated and does not represent a universal legal retention requirement.

The DSAR identity-verification step is simulated and is not a production authentication mechanism.

Passing automated checks demonstrates that the configured rules passed. It does not guarantee that the dataset is error-free, privacy-compliant, or suitable for every downstream use.

---

## Tools

**Python · pandas · Regular Expressions · Data Quality Validation · Statistical Sampling · PII Review · Privacy Operations · Git**
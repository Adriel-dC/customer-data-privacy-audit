\# PII Incident Response Workflow



\## Objective



Define a repeatable process for handling suspected exposure of personally identifiable information (PII) in business datasets.



This workflow is designed for a data analyst's role in detection, containment, evidence preservation, escalation, remediation support, and validation.



Legal notification decisions remain with the appropriate privacy, legal, security, or compliance teams.



\## 1. Detect



Identify the suspected PII exposure through:



\- Automated pattern detection

\- Data quality checks

\- Manual review

\- User or business reports

\- Unexpected values in free-text fields



Record:



\- Detection timestamp

\- Dataset and field

\- Record identifiers

\- PII type

\- Detection method



\## 2. Contain



Reduce further exposure while preserving evidence.



Possible actions include:



\- Stop downstream use of the affected dataset

\- Restrict access to affected outputs

\- Prevent additional exports or reports

\- Isolate affected records

\- Avoid creating unnecessary copies of the exposed data



Raw evidence should not be deleted before the incident is properly assessed.



\## 3. Assess



Determine the scope and severity of the issue.



Assess:



\- Type of PII involved

\- Number of affected records

\- Source system

\- Affected fields

\- Whether data was exported or shared

\- Who or which systems may have accessed it

\- Duration of exposure

\- Whether the issue is isolated or systemic



\## 4. Escalate



Report the incident through the organization's approved incident process.



Depending on company policy, relevant roles may include:



\- Data owner

\- Data engineering

\- Information security

\- Privacy team or Data Protection Officer

\- Legal

\- Compliance



The analyst provides evidence and technical findings.



Privacy, legal, security, and compliance teams determine notification obligations and regulatory actions when required.



\## 5. Remediate



Correct the data issue according to the approved remediation plan.



Possible actions include:



\- Redact PII from free-text fields

\- Mask sensitive values

\- Remove unauthorized copies

\- Correct source-system validation

\- Restrict field access

\- Update ingestion or transformation rules



The remediation should address both the exposed records and the root cause.



\## 6. Validate



After remediation:



\- Re-run PII detection

\- Re-run data quality checks

\- Confirm affected outputs were corrected

\- Confirm downstream datasets no longer expose the identified values

\- Verify the new control prevents recurrence



A successful script execution alone is not sufficient evidence.



Validation results should be recorded.



\## 7. Document and Close



Maintain an audit record containing:



\- Incident identifier

\- Detection timestamp

\- Affected dataset

\- PII type

\- Number of affected records

\- Containment action

\- Escalation path

\- Root cause

\- Remediation

\- Validation result

\- Closure status



The incident should only be considered technically resolved after remediation has been validated.



\## Decision Principle



Detection does not automatically mean deletion.



The correct response is:



Detect -> Contain -> Assess -> Escalate -> Remediate -> Validate -> Document



This preserves evidence, reduces exposure, supports regulatory review, and helps prevent recurrence.


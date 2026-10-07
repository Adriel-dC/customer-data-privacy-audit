\# Statistical and Risk-Based Sampling Strategy



\## Objective



Design a review sample that provides broad representation of the dataset while increasing the probability of detecting high-risk data quality issues.



\## Population



The processed support ticket dataset contains 982 records across four business categories:



\- Account: 267

\- Subscription: 255

\- Billing: 231

\- Technical: 229



\## Statistical Sample Size



For this review, the following parameters were selected:



\- Confidence level: 95%

\- Margin of error: 5%

\- Expected proportion: 50%



A 50% expected proportion is used as a conservative assumption when the true error rate is unknown.



The calculation also applies a finite population correction because the population contains 982 records.



Calculated sample size: 277 records.



These parameters are not universal thresholds. In a production environment, they should be adjusted based on business risk, review cost, regulatory requirements, and the consequences of missing an error.



\## Stratified Sampling



The 277 records are allocated proportionally across ticket categories.



| Category | Population | Sample |

|---|---:|---:|

| Account | 267 | 75 |

| Subscription | 255 | 72 |

| Billing | 231 | 65 |

| Technical | 229 | 65 |

| Total | 982 | 277 |



This prevents larger categories from dominating the review while maintaining approximately proportional representation.



\## Risk-Based Sampling



Statistical sampling alone may miss rare but important problems.



The pipeline therefore identifies records with existing risk indicators, including:



\- Invalid or missing dates

\- Unknown customers

\- Conflicting customer information

\- Missing comments



Six high-risk records were identified.



None of these six records were selected by the stratified random sample.



All six were therefore added as targeted risk records, increasing the final review set from 277 to 283 records.



This demonstrates why random sampling and targeted risk-based review serve different purposes.



\## Review Strategy



The review process combines:



1\. Statistical sample size calculation

2\. Proportional stratification

3\. Random selection within each stratum

4\. Targeted inclusion of known high-risk records



If a reviewed stratum shows an error rate above the agreed acceptance threshold, the sample for that stratum should be expanded.



For critical or systemic issues, the process can escalate from sampling to a full review.



\## Decision Principle



Random sampling provides representative coverage.



Stratification ensures important business groups are represented.



Targeted sampling increases the probability of finding known or suspected high-risk conditions.



These methods are complementary and should not be treated as substitutes for one another.


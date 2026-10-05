# Contact Detail Detection Review

## Scope
This personal project uses synthetic customer and support data.
Email and phone detection uses regular expressions.

## Review method
Twenty comments were labeled with AI assistance based on their
content. The sample includes 10 flagged comments, 9 unflagged
comments, and one deliberately selected invoice example.

This targeted sample is not representative of the full dataset.
The labels are not an independent human benchmark.

## Results
| Contact type | True positives | False positives | False negatives | True negatives |
| --- | ---: | ---: | ---: | ---: |
| Email | 5 | 0 | 0 | 15 |
| Phone | 5 | 1 | 0 | 14 |

## Main finding
Ticket T00056 contains invoice number 1234567890.
The phone pattern flagged it because it contains ten digits.
The comment context identifies it as an invoice number.

## Recommendation
Treat pattern matches as candidates for review.
Check context before classifying ambiguous numbers as phones.

## Limitations
These results apply only to the reviewed sample.
The checks cover email addresses and phone numbers, not all PII.
No missed matches were found in this sample, but that does not
establish complete detection across the dataset.
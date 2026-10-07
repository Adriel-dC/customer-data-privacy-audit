\# Join Cardinality and Fanout Prevention Strategy



\## Objective



Prevent incorrect row multiplication and metric inflation when joining business datasets.



\## Validation Before a Join



Before joining tables, the pipeline validates:



\- Expected grain of each table

\- Uniqueness of keys on the parent/dimension side

\- Number of distinct keys

\- Duplicate-key counts

\- Referential integrity

\- Expected relationship cardinality



For the customer and support ticket model:



\- `customers` has one row per `customer\_id`

\- `support\_tickets` can contain multiple rows per `customer\_id`

\- Expected relationship: one-to-many from customers to tickets

\- Analytical grain after the join: one row per support ticket



The merge uses:



`validate="many\_to\_one"`



This prevents an unexpected duplicate key on the customer side from silently creating fanout.



\## Post-Join Validation



After the join, the pipeline compares:



\- Row count before the join

\- Row count after the join

\- Row-count delta

\- Expected fact-table grain



A row-count increase is investigated before the dataset is approved.



\## Controlled Fanout Test



A duplicate customer key is intentionally introduced in memory.



The validator detects that the parent key is no longer unique and blocks the join before fanout occurs.



This test demonstrates that cardinality controls fail safely.



\## Choosing the Correct Fix



A many-to-many relationship should not automatically be solved by removing duplicates.



\### Deduplication



Use when duplicate records are data quality errors and one record should exist for each business key.



\### Pre-Aggregation



Use when the secondary table contains multiple valid records but the analysis only requires a summarized value at the target grain.



\### Change of Grain



Use when the analysis requires the more detailed relationship and the fact table should legitimately contain multiple rows.



\### Bridge Table



Use when a many-to-many relationship is a real business relationship.



For example, if a support ticket can have multiple tags and each tag can belong to multiple tickets:



`fact\_support\_ticket -> bridge\_ticket\_tag -> dim\_tag`



The bridge table stores the valid ticket-to-tag relationships without duplicating measures in the main fact table.



\## Acceptance Criteria



A join is approved only when:



\- Required parent keys are unique

\- Foreign keys satisfy referential-integrity rules

\- The declared cardinality is valid

\- The resulting row count matches the expected grain

\- Business measures are not unintentionally multiplied



Critical cardinality failures block the dataset from moving to the reporting layer.


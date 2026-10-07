from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

customers = pd.read_csv(
    PROJECT_ROOT / "data/processed/customers_clean.csv",
    dtype="string",
)

tickets = pd.read_csv(
    PROJECT_ROOT / "data/processed/support_tickets_clean.csv",
    dtype="string",
)


def duplicate_key_count(df, key):
    return int(df[key].duplicated(keep=False).sum())


def unmatched_key_count(child, parent, key):
    return int(
        (~child[key].isin(parent[key])).sum()
    )


def validate_one_to_many(
    parent,
    child,
    key,
    relationship_name,
):
    print(f"\nRELATIONSHIP: {relationship_name}")
    print("=" * 70)

    parent_rows = len(parent)
    child_rows = len(child)

    parent_unique_keys = parent[key].nunique(dropna=True)
    child_unique_keys = child[key].nunique(dropna=True)

    parent_duplicates = duplicate_key_count(parent, key)
    unmatched_children = unmatched_key_count(
        child,
        parent,
        key,
    )

    print(f"Parent rows: {parent_rows}")
    print(f"Parent unique keys: {parent_unique_keys}")
    print(f"Parent duplicate-key rows: {parent_duplicates}")
    print(f"Child rows: {child_rows}")
    print(f"Child unique keys: {child_unique_keys}")
    print(f"Unmatched child keys: {unmatched_children}")

    if parent_duplicates > 0:
        print(
            "\nFAIL: Parent key is not unique."
        )
        print(
            "Joining could create fanout."
        )
        return False

    if unmatched_children > 0:
        print(
            "\nFAIL: Referential integrity violation."
        )
        return False

    joined = child.merge(
        parent,
        on=key,
        how="left",
        validate="many_to_one",
        suffixes=("_ticket", "_customer"),
    )

    row_delta = len(joined) - child_rows

    print(f"Rows before join: {child_rows}")
    print(f"Rows after join: {len(joined)}")
    print(f"Row delta: {row_delta}")

    if row_delta != 0:
        print(
            "\nFAIL: Join changed the expected fact-table grain."
        )
        return False

    print(
        "\nPASS: Relationship is many-to-one from "
        "tickets to customers."
    )
    print(
        "PASS: Join preserves the ticket-level grain."
    )

    return True


valid = validate_one_to_many(
    parent=customers,
    child=tickets,
    key="customer_id",
    relationship_name="Customers -> Support Tickets",
)

if valid:
    print(
        "\nJOIN STATUS: APPROVED"
    )
else:
    print(
        "\nJOIN STATUS: BLOCKED"
    )

print("\n" + "=" * 70)
print("CONTROLLED FANOUT TEST")
print("=" * 70)

customers_with_duplicate = pd.concat(
    [
        customers,
        customers.iloc[[0]],
    ],
    ignore_index=True,
)

test_valid = validate_one_to_many(
    parent=customers_with_duplicate,
    child=tickets,
    key="customer_id",
    relationship_name="Controlled duplicate-key test",
)

if not test_valid:
    print(
        "\nEXPECTED RESULT: BLOCKED"
    )
    print(
        "Duplicate dimension keys were detected "
        "before the join could create fanout."
    )
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CUSTOMER_ID = "C0491"
REQUEST_ID = "DSAR-2026-001"

customers = pd.read_csv(
    PROJECT_ROOT / "data/processed/customers_clean.csv",
    dtype="string",
)

tickets = pd.read_csv(
    PROJECT_ROOT / "data/processed/support_tickets_clean.csv",
    dtype="string",
)


# --------------------------------------------------
# 1. SIMULATED IDENTITY VERIFICATION
# --------------------------------------------------

identity_verification = "SIMULATED_VERIFIED"

# In a real DSAR process, knowing a customer ID alone
# would not be sufficient identity verification.


# --------------------------------------------------
# 2. LOCATE CUSTOMER DATA
# --------------------------------------------------

customer_records = customers[
    customers["customer_id"] == CUSTOMER_ID
].copy()

ticket_records = tickets[
    tickets["customer_id"] == CUSTOMER_ID
].copy()


# --------------------------------------------------
# 3. CONTROL CHECKS
# --------------------------------------------------

customer_found = len(customer_records) == 1
customer_key_unique = len(customer_records) <= 1

if not customer_key_unique:
    request_status = "BLOCKED_DUPLICATE_CUSTOMER"

elif not customer_found:
    request_status = "NOT_FOUND"

elif identity_verification != "SIMULATED_VERIFIED":
    request_status = "BLOCKED_IDENTITY_NOT_VERIFIED"

else:
    request_status = "READY_FOR_REVIEW"


# --------------------------------------------------
# 4. CREATE PUBLIC ACCESS PACKAGE
# --------------------------------------------------

package_rows = []

if request_status == "READY_FOR_REVIEW":

    customer = customer_records.iloc[0]

    package_rows.append(
        {
            "record_type": "customer_profile",
            "customer_id": CUSTOMER_ID,
            "field": "name",
            "value": "[REDACTED_NAME]",
        }
    )

    package_rows.append(
        {
            "record_type": "customer_profile",
            "customer_id": CUSTOMER_ID,
            "field": "email",
            "value": "[REDACTED_EMAIL]",
        }
    )

    package_rows.append(
        {
            "record_type": "customer_profile",
            "customer_id": CUSTOMER_ID,
            "field": "plan",
            "value": customer["plan"],
        }
    )

    package_rows.append(
        {
            "record_type": "customer_profile",
            "customer_id": CUSTOMER_ID,
            "field": "signup_date",
            "value": customer["signup_date"],
        }
    )

    for _, ticket in ticket_records.iterrows():
        package_rows.append(
            {
                "record_type": "support_ticket",
                "customer_id": CUSTOMER_ID,
                "field": "ticket_reference",
                "value": (
                    f"{ticket['ticket_id']} | "
                    f"{ticket['created_at']} | "
                    f"{ticket['category']}"
                ),
            }
        )


access_package = pd.DataFrame(package_rows)

package_path = (
    PROJECT_ROOT
    / "reports/dsar_access_package.csv"
)

access_package.to_csv(
    package_path,
    index=False,
)


# --------------------------------------------------
# 5. AUDIT LOG
# --------------------------------------------------

dsar_log = pd.DataFrame(
    [
        {
            "request_id": REQUEST_ID,
            "requested_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "request_type": "ACCESS",
            "customer_id": CUSTOMER_ID,
            "identity_verification": identity_verification,
            "customer_records_found": len(
                customer_records
            ),
            "ticket_records_found": len(
                ticket_records
            ),
            "status": request_status,
        }
    ]
)

log_path = (
    PROJECT_ROOT
    / "reports/dsar_request_log.csv"
)

dsar_log.to_csv(
    log_path,
    index=False,
)


# --------------------------------------------------
# 6. OUTPUT
# --------------------------------------------------

print("\nDSAR ACCESS REQUEST")
print("=" * 75)

print(f"Request ID: {REQUEST_ID}")
print(f"Customer ID: {CUSTOMER_ID}")

print(
    f"Identity verification: "
    f"{identity_verification}"
)

print(
    f"Customer records found: "
    f"{len(customer_records)}"
)

print(
    f"Related tickets found: "
    f"{len(ticket_records)}"
)

print(f"\nREQUEST STATUS: {request_status}")

if request_status == "READY_FOR_REVIEW":
    print(
        "PASS: Customer data was located across "
        "the relevant datasets."
    )

    print(
        "PASS: Public access package created "
        "with direct identifiers redacted."
    )
else:
    print(
        "BLOCKED: Access package should not be "
        "released."
    )

print(
    "\nCONTROL: Identity verification is simulated."
)

print(
    "A real DSAR requires an approved identity "
    "verification process before disclosure."
)

print(
    "CONTROL: Name and email are redacted from "
    "the public portfolio artifact."
)

print(
    "\nSaved: reports/dsar_access_package.csv"
)

print(
    "Saved: reports/dsar_request_log.csv"
)
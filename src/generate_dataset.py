from pathlib import Path
import random

import pandas as pd

# Use a fixed seed to make the dataset reproducible.
rng = random.Random(42)

# Locate the project root from this script.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Create the folders for data and reports.
for folder in ["data/raw", "data/processed", "reports"]:
    (PROJECT_ROOT / folder).mkdir(parents=True, exist_ok=True)

print("Project folders created.")

first_names = ["Emma", "James", "Olivia", "Noah", "Ava", "Liam",
               "Sophia", "Lucas", "Mia", "Ethan"]

last_names = ["Smith", "Johnson", "Brown", "Wilson", "Taylor",
              "Clark", "Lewis", "Walker", "Hall", "Young"]

customers = []

for number in range(1, 501):
    first_name = rng.choice(first_names)
    last_name = rng.choice(last_names)

    signup_date = (
        pd.Timestamp("2025-01-01")
        + pd.Timedelta(days=rng.randint(0, 364))
    )

    customers.append({
        "customer_id": f"C{number:04d}",
        "name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{number}@example.com",
        "plan": rng.choice(["Basic", "Pro", "Premium"]),
        "signup_date": signup_date.strftime("%Y-%m-%d"),
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    PROJECT_ROOT / "data/raw/customers.csv",
    index=False,
)

print(f"Customers saved: {len(customers_df)}")


message_templates = {
    "Billing": [
        "I was charged twice for my subscription.",
        "Could you send me the invoice for this month?",
        "The discount was not applied to my payment.",
    ],
    "Account": [
        "I cannot log in after resetting my password.",
        "How can I update my account details?",
        "I would like to close my account.",
    ],
    "Technical": [
        "The app closes when I try to upload a file.",
        "My dashboard has not updated since yesterday.",
        "I get an error when exporting my report.",
    ],
    "Subscription": [
        "How can I upgrade to the Pro plan?",
        "Please cancel my subscription before renewal.",
        "What features are included in the Premium plan?",
    ],
}

tickets = []

for number in range(1, 1001):
    customer = rng.choice(customers)
    category = rng.choice(list(message_templates))

    created_at = (
        pd.Timestamp(customer["signup_date"])
        + pd.Timedelta(days=rng.randint(0, 90))
        + pd.Timedelta(minutes=rng.randint(0, 1439))
    )

    tickets.append({
        "ticket_id": f"T{number:05d}",
        "customer_id": customer["customer_id"],
        "created_at": created_at.isoformat(),
        "category": category,
        "comment": rng.choice(message_templates[category]),
    })

tickets_df = pd.DataFrame(tickets)

tickets_df.to_csv(
    PROJECT_ROOT / "data/raw/support_tickets.csv",
    index=False,
)

print(f"Support tickets saved: {len(tickets_df)}")

# Introduce controlled quality issues into the synthetic data.
customers_df.loc[10:17, "email"] = None
customers_df.loc[30:34, "email"] = "invalid-email"

# Add three exact duplicates.
exact_duplicates = customers_df.iloc[[50, 100, 150]].copy()

# Add two records with the same ID but conflicting plans.
conflicting_duplicates = customers_df.iloc[[200, 250]].copy()
conflicting_duplicates["plan"] = conflicting_duplicates["plan"].map({
    "Basic": "Pro",
    "Pro": "Premium",
    "Premium": "Basic",
})

customers_df = pd.concat(
    [customers_df, exact_duplicates, conflicting_duplicates],
    ignore_index=True,
)

# Introduce missing references, empty comments, and invalid dates.
for index in range(10):
    tickets_df.loc[index, "customer_id"] = f"UNKNOWN{index:03d}"

tickets_df.loc[20:25, "comment"] = None
tickets_df.loc[40:43, "created_at"] = "2025-02-30T10:00:00"

# Add three exact duplicate tickets.
tickets_df = pd.concat(
    [tickets_df, tickets_df.iloc[[100, 300, 500]].copy()],
    ignore_index=True,
)

# Save the audit inputs with the controlled issues included.
customers_df.to_csv(
    PROJECT_ROOT / "data/raw/customers.csv", index=False
)
tickets_df.to_csv(
    PROJECT_ROOT / "data/raw/support_tickets.csv", index=False
)

print(f"Final customer rows: {len(customers_df)}")
print(f"Final ticket rows: {len(tickets_df)}")


# Select original tickets without changing the exact duplicates.
eligible_indices = [
    index for index in range(60, 1000)
    if index not in [100, 300, 500]
]
pii_indices = rng.sample(eligible_indices, 60)

for position, index in enumerate(pii_indices):
    email = f"customer.{index}@example.com"

    # Use fictional numbers with different formatting.
    suffix = f"{100 + position:04d}"
    phone = [
        f"+1 202-555-{suffix}",
        f"(202) 555-{suffix}",
        f"202555{suffix}",
    ][position % 3]

    if position < 30:
        contact_details = f" Please reply to {email}."
    elif position < 50:
        contact_details = f" Please call me on {phone}."
    else:
        contact_details = f" Contact me at {email} or {phone}."

    tickets_df.loc[index, "comment"] += contact_details

# Include numbers that should not be mistaken for phone numbers.
tickets_df.loc[55, "comment"] = (
    "Please check invoice 1234567890. I was charged twice."
)

tickets_df.to_csv(
    PROJECT_ROOT / "data/raw/support_tickets.csv",
    index=False,
)

print("Contact details added to 60 synthetic comments.")
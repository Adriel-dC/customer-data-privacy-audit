from pathlib import Path
from statistics import NormalDist
import math
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

tickets = pd.read_csv(
    PROJECT_ROOT / "data/processed/support_tickets_clean.csv",
    dtype="string",
)

CONFIDENCE_LEVEL = 0.95
MARGIN_OF_ERROR = 0.05
EXPECTED_PROPORTION = 0.50
RANDOM_SEED = 42


def calculate_sample_size(
    population_size,
    confidence_level=CONFIDENCE_LEVEL,
    margin_of_error=MARGIN_OF_ERROR,
    expected_proportion=EXPECTED_PROPORTION,
):
    """
    Calculate sample size for a proportion using a finite
    population correction.

    expected_proportion=0.50 is conservative because it produces
    the largest sample requirement when the true rate is unknown.
    """

    z_score = NormalDist().inv_cdf(
        1 - (1 - confidence_level) / 2
    )

    p = expected_proportion
    e = margin_of_error

    initial_sample = (
        (z_score ** 2)
        * p
        * (1 - p)
        / (e ** 2)
    )

    corrected_sample = (
        initial_sample
        / (
            1
            + ((initial_sample - 1) / population_size)
        )
    )

    return math.ceil(corrected_sample)


def proportional_allocation(
    dataframe,
    group_column,
    total_sample_size,
):
    counts = dataframe[group_column].value_counts()

    exact_allocation = (
        counts / len(dataframe) * total_sample_size
    )

    allocation = (
        exact_allocation
        .apply(math.floor)
        .astype(int)
    )

    remaining = (
        total_sample_size - allocation.sum()
    )

    fractions = (
        exact_allocation - allocation
    ).sort_values(ascending=False)

    for group in fractions.index[:remaining]:
        allocation[group] += 1

    return allocation


def create_stratified_sample(
    dataframe,
    group_column,
    allocation,
):
    samples = []

    for group, sample_size in allocation.items():
        group_data = dataframe[
            dataframe[group_column] == group
        ]

        sample = group_data.sample(
            n=sample_size,
            random_state=RANDOM_SEED,
        )

        samples.append(sample)

    return pd.concat(
        samples,
        ignore_index=True,
    )


population_size = len(tickets)

sample_size = calculate_sample_size(
    population_size
)

allocation = proportional_allocation(
    tickets,
    "category",
    sample_size,
)

stratified_sample = create_stratified_sample(
    tickets,
    "category",
    allocation,
)


# Identify higher-risk records separately.
risk_columns = [
    "date_invalid_or_missing",
    "customer_unknown",
    "customer_conflicting",
    "comment_missing",
]

risk_mask = pd.Series(
    False,
    index=tickets.index,
)

for column in risk_columns:
    values = (
        tickets[column]
        .fillna("false")
        .str.strip()
        .str.lower()
    )

    risk_mask |= values.eq("true")

high_risk_records = tickets[risk_mask].copy()


# Add risk records that were not already selected.
sample_ticket_ids = set(
    stratified_sample["ticket_id"]
)

targeted_risk_records = high_risk_records[
    ~high_risk_records["ticket_id"].isin(
        sample_ticket_ids
    )
].copy()

combined_review_sample = pd.concat(
    [
        stratified_sample.assign(
            sampling_reason="stratified_random"
        ),
        targeted_risk_records.assign(
            sampling_reason="targeted_risk"
        ),
    ],
    ignore_index=True,
)


# Save outputs.
stratified_sample.to_csv(
    PROJECT_ROOT
    / "reports/stratified_review_sample.csv",
    index=False,
)

combined_review_sample.to_csv(
    PROJECT_ROOT
    / "reports/combined_review_sample.csv",
    index=False,
)


print("\nSAMPLING STRATEGY")
print("=" * 70)

print(f"Population size: {population_size}")
print(
    f"Confidence level: "
    f"{CONFIDENCE_LEVEL:.0%}"
)
print(
    f"Margin of error: "
    f"{MARGIN_OF_ERROR:.0%}"
)
print(
    f"Calculated sample size: "
    f"{sample_size}"
)

print("\nSTRATIFIED ALLOCATION")
print("=" * 70)

for category, size in allocation.items():
    population_count = int(
        (tickets["category"] == category).sum()
    )

    print(
        f"{category}: "
        f"{size} sampled from "
        f"{population_count}"
    )

print("\nRISK-BASED REVIEW")
print("=" * 70)

print(
    f"High-risk records found: "
    f"{len(high_risk_records)}"
)

print(
    f"High-risk records already in "
    f"random sample: "
    f"{len(high_risk_records) - len(targeted_risk_records)}"
)

print(
    f"Additional targeted risk records: "
    f"{len(targeted_risk_records)}"
)

print(
    f"Final combined review size: "
    f"{len(combined_review_sample)}"
)

print(
    "\nSaved: "
    "reports/stratified_review_sample.csv"
)

print(
    "Saved: "
    "reports/combined_review_sample.csv"
)
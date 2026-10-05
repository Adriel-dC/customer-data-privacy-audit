from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
review = pd.read_csv(
    PROJECT_ROOT / "reports/manual_review_labeled.csv",
    sep=";",
    dtype="string",
)

# Validate labels before calculating results.
label_columns = [
    "detected_email", "detected_phone",
    "actual_email", "actual_phone",
]

for column in label_columns:
    labels = review[column].str.strip().str.lower()
    if not labels.isin(["true", "false"]).all():
        raise ValueError(f"Missing or invalid labels in {column}")
    review[column] = labels.eq("true")

print(f"Reviewed comments: {len(review)}")
print("Review method: AI-assisted labeling")
print("Targeted sample; results do not represent the full dataset.")

results = []

for contact_type in ["email", "phone"]:
    detected = review[f"detected_{contact_type}"]
    actual = review[f"actual_{contact_type}"]

    tp = int((detected & actual).sum())
    fp = int((detected & ~actual).sum())
    fn = int((~detected & actual).sum())
    tn = int((~detected & ~actual).sum())

    results.append({
        "contact_type": contact_type,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    })

    print(f"\n--- {contact_type.title()} detection ---")
    print(f"True positives: {tp}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")
    print(f"True negatives: {tn}")

metrics = pd.DataFrame(results)
metrics.to_csv(
    PROJECT_ROOT / "reports/detection_metrics.csv",
    index=False,
)

disagreements = review[
    (review["detected_email"] != review["actual_email"])
    | (review["detected_phone"] != review["actual_phone"])
]
disagreements.to_csv(
    PROJECT_ROOT / "reports/detection_disagreements.csv",
    index=False,
)

print("\nMetrics and disagreements saved in reports.")
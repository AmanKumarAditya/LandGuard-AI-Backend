
import pandas as pd
import numpy as np

np.random.seed(42)
n = 500

df = pd.DataFrame({
    "land_area": np.random.uniform(10, 500, n),
    "number_of_landowners": np.random.randint(5, 300, n),
    "pending_approvals": np.random.randint(0, 15, n),
    "legal_disputes": np.random.randint(0, 20, n),
    "compensation_percentage": np.random.uniform(10, 100, n),
    "project_progress": np.random.uniform(5, 100, n),
})

risk_score = (
    df["pending_approvals"] * 2.5
    + df["legal_disputes"] * 3
    + (100 - df["compensation_percentage"]) * 0.25
    + (100 - df["project_progress"]) * 0.15
    + np.random.normal(0, 8, n)
)

# Synthetic demonstration threshold
threshold = risk_score.median()

df["delay_days"] = np.maximum(
    0, 30 + (risk_score - threshold) * 1.5
).round().astype(int)

df["delayed"] = (df["delay_days"] > 30).astype(int)

df.to_csv("data/land_acquisition_data.csv", index=False)

print("Balanced demonstration dataset created!")
print(df["delayed"].value_counts())


import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("data/land_acquisition_data.csv")

# Select input features
X = df[
    [
        "land_area",
        "number_of_landowners",
        "pending_approvals",
        "legal_disputes",
        "compensation_percentage",
        "project_progress"
    ]
]

# Target variable
y = df["delayed"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("LandGuard AI Model Training Complete!")
print("Test accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save trained model
joblib.dump(model, "landguard_model.pkl")

print("\nModel saved as landguard_model.pkl")

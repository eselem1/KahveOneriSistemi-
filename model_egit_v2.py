import json, joblib, pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# === Veri setini yükle ===
with open("coffee_recommendation_dataset_v7_logic_fixed.json",
          encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["target"] = df["recommendation"].str[0]      # ilk öneriyi hedef etiket seç

feature_cols = ["sweetness", "bitterness", "milk", "milk_type",
                "caffeine", "temperature", "size", "flavor"]

X, y = df[feature_cols], df["target"]

pipe = Pipeline([
    ("prep", ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), feature_cols)]
    )),
    ("clf", RandomForestClassifier(
        n_estimators=300, random_state=42, n_jobs=-1
    ))
])

pipe.fit(X, y)
joblib.dump(pipe, "coffee_recommendation_model_v2.joblib")
print("✅ Model güncellendi & kaydedildi → coffee_recommendation_model_v2.joblib")

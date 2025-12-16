import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Simple sample data
data = {
    "hour": [1, 5, 10, 15, 20, 24],
    "demand": [120, 200, 300, 450, 500, 600]
}

df = pd.DataFrame(data)

X = df[["hour"]]
y = df["demand"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "backend/ml/models/model.pkl")
print("✅ Model trained and saved")

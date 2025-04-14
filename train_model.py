import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
df = pd.read_csv("D:/Final Insta Detection/IJECE_df_train.csv")  # Make sure path is correct

# Select features (removed avgtime and pr)
features = [
    'nmedia', 'nfollower', 'nfollowing',
    'pic', 'url',
    'followerToFollowing', 'hasMedia'
]
target = 'fake'

# Prepare data
X = df[features]
y = df[target]

# Handle missing values
X = X.fillna(0)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train XGBoost Classifier
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Make predictions and evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Save trained model
with open("xgb_fake_account_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as xgb_fake_account_model.pkl")

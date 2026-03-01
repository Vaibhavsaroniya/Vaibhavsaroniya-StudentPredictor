import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

data = pd.read_csv(r"C:\JAVA\StudentPredictor\students.csv")
print("✅ Data loaded!")

X = data[["attendance", "study_hours", "past_grade"]]
y = data["result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("✅ Data split done!")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("✅ Model trained!")

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {acc * 100:.2f}%")

pickle.dump(model, open(r"C:\JAVA\StudentPredictor\model.pkl", "wb"))
print("✅ Model saved!")

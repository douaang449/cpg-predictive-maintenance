from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
import os

from preprocess import load_and_clean, FEATURES


def train_baseline(csv_path: str ="data/ai4i2020.csv", model_out: str = "data/baseline_rf.joblib"):
    df = load_and_clean(csv_path)
    X  = df[FEATURES]
    y =df["failure"]

    X_train , X_test, y_train ,y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    print("=== Rapport de classification ===")
    print(classification_report(y_test, y_pred, digits=3, target_names=["Normal", "Panne"]))
    print(f"ROC-AUC : {roc_auc_score(y_test, y_proba):.3f}")
    print(f"\nMatrice de confusion :\n{confusion_matrix(y_test, y_pred)}")

    print("\n=== Importance des features === ")
    for feat, imp in sorted(zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1]):
        print(f" {feat}, {imp:.3f}")

    os.makedirs(os.path.dirname(model_out), exist_ok=True)
    joblib.dump(clf, model_out)
    print(f"\nModèle sauvegardé : {model_out}")
    return clf

if __name__ == "__main__":
    train_baseline()    

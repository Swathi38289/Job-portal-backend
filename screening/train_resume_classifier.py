import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def train(input_csv: Path, output_model: Path) -> dict:
    data = pd.read_csv(
        input_csv,
        usecols=["Resume_str", "Category"],
        low_memory=False,
    ).dropna(subset=["Resume_str", "Category"])
    data["Resume_str"] = data["Resume_str"].astype(str)

    texts_train, texts_test, labels_train, labels_test = train_test_split(
        data["Resume_str"],
        data["Category"],
        test_size=0.2,
        random_state=42,
        stratify=data["Category"],
    )
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english", max_features=50000)),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(texts_train, labels_train)
    predictions = model.predict(texts_test)

    output_model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_model)
    report = classification_report(
        labels_test, predictions, output_dict=True, zero_division=0
    )
    metrics = {
        "rows": len(data),
        "categories": int(data["Category"].nunique()),
        "test_accuracy": round(accuracy_score(labels_test, predictions), 4),
        "classification_report": report,
    }
    output_model.with_suffix(".metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a resume category classifier.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_model", type=Path)
    arguments = parser.parse_args()
    result = train(arguments.input_csv, arguments.output_model)
    print(json.dumps({key: result[key] for key in ("rows", "categories", "test_accuracy")}))
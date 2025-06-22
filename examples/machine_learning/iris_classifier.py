"""Iris classifier example.

This demonstrates a machine learning workflow including data loading,
model training, and evaluation.
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def load_data() -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """Load and prepare the Iris dataset."""
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names.tolist()
    return X, y, feature_names, target_names


def preprocess_data(
    X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into training and testing sets."""
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_estimators: int = 100,
    random_state: int = 42,
) -> RandomForestClassifier:
    """Train a Random Forest classifier."""
    model = RandomForestClassifier(
        n_estimators=n_estimators, random_state=random_state
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(
    model: RandomForestClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
    target_names: List[str],
) -> Dict[str, float]:
    """Evaluate model performance and return metrics."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
    }
    
    # Add classification report metrics
    report = classification_report(
        y_test, y_pred, target_names=target_names, output_dict=True
    )
    
    # Flatten the report for easier access
    for label, scores in report.items():
        if isinstance(scores, dict):
            for metric, value in scores.items():
                metrics[f"{label}_{metric}"] = value
        else:
            metrics[label] = scores
    
    return metrics


def save_model(model, output_dir: str = "output") -> str:
    """Save the trained model.
    
    Args:
        model: Trained model to save
        output_dir: Directory to save the model
        
    Returns:
        Path to the saved model
    """
    import joblib  # Import here to make it optional
    
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "iris_classifier.joblib")
    joblib.dump(model, model_path)
    return model_path


def train_iris() -> Dict[str, Union[float, str]]:
    """Train and evaluate an Iris classifier.
    
    Example:
        python -m examples.machine_learning.iris_classifier
    """
    print("Loading Iris dataset...")
    X, y, feature_names, target_names = load_data()
    
    print("Splitting data into training and test sets...")
    X_train, X_test, y_train, y_test = preprocess_data(X, y)
    
    print("Training Random Forest classifier...")
    model = train_model(X_train, y_train)
    
    print("Evaluating model...")
    metrics = evaluate_model(model, X_test, y_test, target_names)
    
    print("Saving model...")
    model_path = save_model(model)
    metrics["model_path"] = model_path
    
    print("\nTraining complete!")
    print(f"Model saved to: {model_path}")
    print("\nMetrics:")
    for k, v in metrics.items():
        if k != "model_path":  # Don't print the model path in metrics
            print(f"{k}: {v}")
    
    return metrics


if __name__ == "__main__":
    # When run directly, train the model
    train_iris()

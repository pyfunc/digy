"""
Iris Classifier Example

This script demonstrates a simple machine learning workflow using the Iris dataset.
It trains a classifier and evaluates its performance.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    confusion_matrix, 
    ConfusionMatrixDisplay
)

def load_data():
    """Load and prepare the Iris dataset."""
    print("📊 Loading Iris dataset...")
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='target')
    target_names = iris.target_names
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    return X_train, X_test, y_train, y_test, target_names

def train_model(X_train, y_train, n_estimators=100, random_state=42):
    """Train a Random Forest classifier."""
    print("🤖 Training model...")
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test, target_names, output_dir='output'):
    """Evaluate the model and save results."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    
    # Save metrics
    metrics = {
        'accuracy': accuracy,
        'classification_report': report
    }
    
    with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Plot confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
    disp.plot(cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), bbox_inches='tight')
    
    # Save feature importances
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title('Feature Importances')
    plt.bar(range(X_test.shape[1]), importances[indices])
    plt.xticks(range(X_test.shape[1]), [X_test.columns[i] for i in indices], rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importances.png'))
    
    return metrics

def save_model(model, output_dir='output'):
    """Save the trained model."""
    Path(output_dir).mkdir(exist_ok=True)
    model_path = os.path.join(output_dir, 'iris_classifier.joblib')
    joblib.dump(model, model_path)
    return model_path

def main(output_dir='output'):
    """Main function to run the ML workflow."""
    # Load and prepare data
    X_train, X_test, y_train, y_test, target_names = load_data()
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, target_names, output_dir)
    
    # Save model
    model_path = save_model(model, output_dir)
    
    print(f"✅ Model training complete!")
    print(f"📊 Accuracy: {metrics['accuracy']:.4f}")
    print(f"💾 Model saved to {model_path}")
    print(f"📈 Results saved to {output_dir}/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train an Iris classifier')
    parser.add_argument('--output-dir', default='output', 
                       help='Directory to save output files')
    
    args = parser.parse_args()
    main(args.output_dir)

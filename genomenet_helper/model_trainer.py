import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os
import logging

logging.basicConfig(level=logging.INFO)

def train_model(train_files, test_files, n_estimators=100):
    # Load training and testing data
    train_data = pd.concat([pd.read_csv(file) for file in train_files], ignore_index=True)
    test_data = pd.concat([pd.read_csv(file) for file in test_files], ignore_index=True)

    # Check if the datasets are empty
    if train_data.empty or test_data.empty:
        logging.error("Training or testing dataset is empty.")
        return

    # Fill NaN values with zeros
    train_data.fillna(0, inplace=True)
    test_data.fillna(0, inplace=True)

    # Prepare training and testing sets
    X_train = train_data.drop(['unique_id', 'file_name', 'sample_id', 'class'], axis=1)
    y_train = train_data['class']
    X_test = test_data.drop(['unique_id', 'file_name', 'sample_id', 'class'], axis=1)
    y_test = test_data['class']

    # Train the model
    classifier = RandomForestClassifier(n_estimators=n_estimators, random_state=0)
    classifier.fit(X_train, y_train)

    # Evaluate the model
    y_pred = classifier.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Provide a human-readable interpretation
    logging.info("Model Evaluation:")
    for label, metrics in report.items():
        if label == 'accuracy':
            # Handle overall accuracy
            logging.info(f"{label.capitalize()}: {metrics:.2f}")
        elif label in ['macro avg', 'weighted avg']:
            # Handle macro and weighted averages
            logging.info(f"{label.capitalize()} - Precision: {metrics['precision']:.2f}, "
                         f"Recall: {metrics['recall']:.2f}, F1-score: {metrics['f1-score']:.2f}")
        else:
            # Handle individual class metrics
            logging.info(f"Class {label} - Precision: {metrics['precision']:.2f}, "
                         f"Recall: {metrics['recall']:.2f}, F1-score: {metrics['f1-score']:.2f}")


def process_model_training(train_files, test_files):
    train_model(train_files, test_files)

import os
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_curve, auc
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.cm as cm


logging.basicConfig(level=logging.INFO)

def train_model(train_files, test_files, output_path, model_type='random_forest', n_estimators=50, fractions=[1.0, 0.5, 0.25, 0.05, 0.01]):
    train_data_full = pd.concat([pd.read_csv(file) for file in train_files], ignore_index=True)
    test_data = pd.concat([pd.read_csv(file) for file in test_files], ignore_index=True)

    # Balance the test data
    min_class_count_test = test_data['class'].value_counts().min()
    test_data = test_data.groupby('class').apply(lambda x: x.sample(min_class_count_test)).reset_index(drop=True)

    label_encoder = LabelEncoder()
    test_data.fillna(0, inplace=True)
    X_test = test_data.drop(['unique_id', 'file_name', 'sample_id', 'class'], axis=1).apply(pd.to_numeric, errors='coerce').fillna(0)
    y_test = label_encoder.fit_transform(test_data['class'])
    class_names = label_encoder.classes_

    # Assuming the positive class is the second class in alphabetical order
    # Adjust this logic if necessary
    positive_class_index = np.where(label_encoder.classes_ == sorted(label_encoder.classes_)[1])[0][0]

    metrics_df = pd.DataFrame(columns=['Fraction', 'Precision', 'Recall', 'F1-score', 'ROC AUC', 'Samples Per Class'])
    roc_data = {}

    with PdfPages(output_path) as pdf:
        for fraction in fractions:
            # Balance the training data for the current fraction
            min_class_count_train = train_data_full['class'].value_counts().min()
            logging.info(f"min_class_count_train: {min_class_count_train}")

            # Balance the training data for the current fraction
            train_data = train_data_full.groupby('class').apply(lambda x: x.sample(min(int(len(x) * fraction), min_class_count_train), random_state=0)).reset_index(drop=True)
            logging.info(f"Number of rows in the balanced training data: {len(train_data)}")

            train_data.fillna(0, inplace=True)
            X_train = train_data.drop(['unique_id', 'file_name', 'sample_id', 'class'], axis=1).apply(pd.to_numeric, errors='coerce').fillna(0)
            y_train = label_encoder.transform(train_data['class'])
            
            # Count the number of samples per class for the current fraction
            samples_per_class = train_data['class'].value_counts().sort_index().to_dict()

            classifier = RandomForestClassifier(n_estimators=n_estimators, random_state=0, n_jobs=-1)
            classifier.fit(X_train, y_train)

            y_pred = classifier.predict(X_test)
            report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)

            logging.info(f"Model Evaluation for Training Fraction: {fraction}")
            for label, metrics in report.items():
                if label in ['macro avg', 'weighted avg']:
                    logging.info(f"{label.capitalize()} - Precision: {metrics['precision']:.2f}, "
                                 f"Recall: {metrics['recall']:.2f}, F1-score: {metrics['f1-score']:.2f}")

            metrics = report['weighted avg']
            if len(class_names) == 2:
                y_prob = classifier.predict_proba(X_test)[:, positive_class_index]
                fpr, tpr, _ = roc_curve(y_test, y_prob, pos_label=positive_class_index)
                roc_auc = auc(fpr, tpr)
                roc_data[fraction] = (fpr, tpr, roc_auc)
            else:
                roc_auc = np.nan

            new_row = pd.DataFrame({'Fraction': [fraction], 
                            'Precision': [round(metrics['precision'], 2)],
                            'Recall': [round(metrics['recall'], 2)], 
                            'F1-score': [round(metrics['f1-score'], 2)],
                            'ROC AUC': [round(roc_auc, 2) if roc_auc is not np.nan else 'N/A'],
                            'Samples Per Class': [len(train_data)]})
            metrics_df = pd.concat([metrics_df, new_row], ignore_index=True)

            if fraction == 1.0:
                # Predict on test data
                y_pred_test = classifier.predict(X_test)  # Predictions on test data
                # Now create the PCoA plot with test data and predictions
                create_pcoa_plot(X_test, y_test, y_pred_test, class_names, 'PCoA Plot - Test Data', pdf)
            
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.table(cellText=metrics_df.values, colLabels=metrics_df.columns, loc='center')
        pdf.savefig(fig)
        plt.close()

        if roc_data:
            plt.figure()
            line_styles = ['-', '--', '-.', ':', (0, (3, 5, 1, 5))]  # Different line styles
            for i, (frac, (fpr, tpr, roc_auc)) in enumerate(roc_data.items()):
                plt.plot(fpr, tpr, lw=2, label=f'Fraction {frac} - ROC curve (area = {roc_auc:.2f})', linestyle=line_styles[i])
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver Operating Characteristic')
            plt.legend(loc="lower right")
            pdf.savefig()
            plt.close()
        
def create_pcoa_plot(X, y_true, y_pred, class_names, title, pdf):
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(X)
    explained_variance = pca.explained_variance_ratio_ * 100

    plt.figure(figsize=(10, 10))
    colors = ['blue', 'orange']  # Modify colors to match the number of your classes

    # Plotting each class
    for idx, label in enumerate(class_names):
        class_idx = np.where(y_true == idx)[0]
        plt.scatter(principal_components[class_idx, 0], principal_components[class_idx, 1], 
                    label=label, alpha=0.5, edgecolors='w', color=colors[idx])

    # Highlight misclassified samples on the test set
    misclassified = y_true != y_pred
    print(f"Number of misclassified samples: {np.sum(misclassified)}")  # Debug output
    plt.scatter(principal_components[misclassified, 0], principal_components[misclassified, 1], 
                s=50, facecolors='none', edgecolors='r', label='Misclassified', zorder=3)

    plt.title(title)
    plt.xlabel(f'PC1 ({explained_variance[0]:.2f}%)')
    plt.ylabel(f'PC2 ({explained_variance[1]:.2f}%)')
    plt.legend()
    pdf.savefig()
    plt.close()
    
def process_model_training(train_files, test_files, output_path):
     # Check if files exist and are valid CSVs
    for file in train_files + test_files:
        if not os.path.isfile(file) or not file.endswith('.csv'):
            logging.error(f"Invalid file path or format: {file}")
            return
    train_model(train_files, test_files, output_path)



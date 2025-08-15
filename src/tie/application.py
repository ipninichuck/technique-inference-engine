import numpy as np

from tie.constants import PredictionMethod
from tie.engine import TechniqueInferenceEngine
from tie.matrix_builder import ReportTechniqueMatrixBuilder
from tie.recommender import (
    BPRRecommender,
    FactorizationRecommender,
    ImplicitBPRRecommender,
    ImplicitWalsRecommender,
    TopItemsRecommender,
    WalsRecommender,
)


def train_model(
    model_name, dataset_filepath, enterprise_attack_filepath, validation_ratio, test_ratio
):
    """
    Trains a recommender model.

    Args:
        model_name (str): The name of the model to train.
        dataset_filepath (str): Path to the dataset file.
        enterprise_attack_filepath (str): Path to the enterprise attack STIX file.
        validation_ratio (float): Percentage of data for validation.
        test_ratio (float): Percentage of data for testing.

    Returns:
        TechniqueInferenceEngine: The trained Technique Inference Engine.
    """
    data_builder = ReportTechniqueMatrixBuilder(
        combined_dataset_filepath=dataset_filepath,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )
    training_data, test_data, validation_data = data_builder.build_train_test_validation(
        test_ratio, validation_ratio
    )

    model_class, prediction_method, hyperparameters = get_model_config(
        model_name, training_data.m, training_data.n
    )

    model = model_class(
        m=training_data.m,
        n=training_data.n,
        k=hyperparameters.get("embedding_dimension", 10),
    )

    tie = TechniqueInferenceEngine(
        training_data=training_data,
        validation_data=validation_data,
        test_data=test_data,
        model=model,
        prediction_method=prediction_method,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )

    if "epochs" in hyperparameters:
        tie.fit(**hyperparameters)
    else:
        tie.fit()

    return tie


def predict_techniques(tie, techniques):
    """
    Predicts techniques for a given report.

    Args:
        tie (TechniqueInferenceEngine): The trained Technique Inference Engine.
        techniques (list): A list of technique IDs.

    Returns:
        pandas.DataFrame: A DataFrame with the predictions.
    """
    return tie.predict_for_new_report(frozenset(techniques))


def tune_hyperparameters(
    model_name, dataset_filepath, enterprise_attack_filepath, validation_ratio, test_ratio
):
    """
    Tunes hyperparameters for a given model.

    Args:
        model_name (str): The name of the model to tune.
        dataset_filepath (str): Path to the dataset file.
        enterprise_attack_filepath (str): Path to the enterprise attack STIX file.
        validation_ratio (float): Percentage of data for validation.
        test_ratio (float): Percentage of data for testing.

    Returns:
        dict: The best hyperparameters found.
    """
    data_builder = ReportTechniqueMatrixBuilder(
        combined_dataset_filepath=dataset_filepath,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )
    training_data, test_data, validation_data = data_builder.build_train_test_validation(
        test_ratio, validation_ratio
    )

    model_class, prediction_method, _ = get_model_config(
        model_name, training_data.m, training_data.n
    )

    model = model_class(
        m=training_data.m,
        n=training_data.n,
        k=4,  # A common embedding dimension from the notebook
    )

    tie = TechniqueInferenceEngine(
        training_data=training_data,
        validation_data=validation_data,
        test_data=test_data,
        model=model,
        prediction_method=prediction_method,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )

    hyperparameters = get_hyperparameter_space(model_name)
    best_hyperparameters = tie.fit_with_validation(**hyperparameters)

    return best_hyperparameters


def get_hyperparameter_space(model_name):
    """
    Gets the hyperparameter space for a given model.

    Args:
        model_name (str): The name of the model.

    Returns:
        dict: The hyperparameter space for the model.
    """
    spaces = {
        "wals": {
            "epochs": [25],
            "c": [0.001, 0.005, 0.01, 0.05, 0.1, 0.3, 0.5, 0.7],
            "regularization_coefficient": [0.0, 0.00001, 0.0001, 0.001, 0.01],
        },
        "bpr": {
            "epochs": [20],
            "learning_rate": [0.00001, 0.00005, 0.0001, 0.001],
            "regularization": [0.0, 0.0001, 0.001, 0.01],
        },
    }
    return spaces.get(model_name, {})


def get_model_config(model_name, m, n):
    """
    Gets the configuration for a given model.

    Args:
        model_name (str): The name of the model.
        m (int): Number of reports.
        n (int): Number of techniques.

    Returns:
        tuple: A tuple containing the model class, prediction method, and hyperparameters.
    """
    models = {
        "top_items": (
            TopItemsRecommender,
            PredictionMethod.DOT,
            {"embedding_dimension": 10},
        ),
        "factorization": (
            FactorizationRecommender,
            PredictionMethod.DOT,
            {
                "embedding_dimension": 10,
                "epochs": 10,
                "learning_rate": 1.0,
                "regularization_coefficient": 0.001,
                "gravity_coefficient": 0.001,
            },
        ),
        "bpr": (
            BPRRecommender,
            PredictionMethod.COSINE,
            {
                "embedding_dimension": 4,
                "epochs": 25,
                "learning_rate": 0.001,
                "regularization_coefficient": 0.01,
            },
        ),
        "implicit_bpr": (
            ImplicitBPRRecommender,
            PredictionMethod.COSINE,
            {
                "embedding_dimension": 10,
                "epochs": 20,
                "learning_rate": 0.005,
                "regularization_coefficient": 0.0001,
            },
        ),
        "implicit_wals": (
            ImplicitWalsRecommender,
            PredictionMethod.COSINE,
            {
                "embedding_dimension": 10,
                "epochs": 20,
                "c": 0.5,
                "regularization_coefficient": 0.05,
            },
        ),
        "wals": (
            WalsRecommender,
            PredictionMethod.DOT,
            {
                "embedding_dimension": 4,
                "epochs": 25,
                "c": 0.001,
                "regularization_coefficient": 0.00001,
            },
        ),
    }
    return models[model_name]

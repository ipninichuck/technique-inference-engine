"""This module provides a method to make predictions using a pre-trained model."""

import io
import zipfile

import numpy as np

from tie.application import get_model_config
from tie.engine import TechniqueInferenceEngine
from tie.matrix import ReportTechniqueMatrix


def load_model_from_zip(zip_path):
    """
    Loads a model from a zip file.

    Args:
        zip_path (str): The path to the zip file.

    Returns:
        TechniqueInferenceEngine: The loaded Technique Inference Engine.
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("U.npy", "r") as f:
            u_bytes = io.BytesIO(f.read())
        u = np.load(u_bytes, allow_pickle=True)

        with z.open("V.npy", "r") as f:
            v_bytes = io.BytesIO(f.read())
        v = np.load(v_bytes, allow_pickle=True)

        with z.open("technique_ids.npy", "r") as f:
            technique_ids_bytes = io.BytesIO(f.read())
        technique_ids = np.load(technique_ids_bytes, allow_pickle=True)

        with z.open("hyperparameters.npy", "r") as f:
            hyperparameters_bytes = io.BytesIO(f.read())
        hyperparameters = np.load(hyperparameters_bytes, allow_pickle=True).item()

    model_name = hyperparameters.get("model_name", "wals")
    model_class, prediction_method, _ = get_model_config(model_name, u.shape[0], v.shape[0])

    model = model_class(m=u.shape[0], n=v.shape[0], k=u.shape[1])
    model._U = u
    model._V = v

    # We need to create a dummy ReportTechniqueMatrix because the
    # TechniqueInferenceEngine requires it. We will not use it for training.
    dummy_matrix = ReportTechniqueMatrix(
        report_ids=[], technique_ids=technique_ids, matrix=np.array([[]])
    )

    tie = TechniqueInferenceEngine(
        training_data=dummy_matrix,
        validation_data=dummy_matrix,
        test_data=dummy_matrix,
        model=model,
        prediction_method=prediction_method,
        enterprise_attack_filepath="",  # Not needed for prediction
        hyperparameters=hyperparameters,
    )

    return tie


def webtest(techniques, zip_path="src/tie-web-interface/public/app.trained.model.zip"):
    """
    Predicts techniques for a given report using the pre-trained model.

    Args:
        techniques (list): A list of technique IDs.
        zip_path (str): The path to the zip file.

    Returns:
        pandas.DataFrame: A DataFrame with the predictions.
    """
    tie = load_model_from_zip(zip_path)
    return tie.predict_for_new_report(frozenset(techniques))

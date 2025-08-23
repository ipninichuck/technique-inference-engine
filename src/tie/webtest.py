"""This module provides a method to make predictions using a pre-trained model."""

import pickle


def webtest(techniques, pickle_path):
    """
    Predicts techniques for a given report using a pickled model.

    Args:
        techniques (list): A list of technique IDs.
        pickle_path (str): The path to the pickle file.

    Returns:
        pandas.DataFrame: A DataFrame with the predictions.
    """
    with open(pickle_path, "rb") as f:
        tie = pickle.load(f)
    return tie.predict_for_new_report(frozenset(techniques))

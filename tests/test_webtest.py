import io
import zipfile
import unittest
import numpy as np
import pandas as pd

import pickle

from tie.webtest import webtest, load_model_from_zip, webtest_pickle
from tie.engine import TechniqueInferenceEngine
from tie.recommender.wals_recommender import WalsRecommender
from tie.matrix import ReportTechniqueMatrix
from tie.constants import PredictionMethod


class TestWebtest(unittest.TestCase):
    def test_webtest(self):
        # Create dummy data
        u = np.random.rand(10, 4)
        v = np.random.rand(20, 4)
        technique_ids = [f"T{i}" for i in range(20)]
        hyperparameters = {
            "model_name": "wals",
            "c": 0.001,
            "regularization_coefficient": 0.00001,
        }

        # Create a dummy zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            np.save(z.open("U.npy", "w"), u)
            np.save(z.open("V.npy", "w"), v)
            np.save(z.open("technique_ids.npy", "w"), technique_ids)
            np.save(z.open("hyperparameters.npy", "w"), hyperparameters)

        # Write the zip buffer to a file
        with open("test_model.zip", "wb") as f:
            f.write(zip_buffer.getvalue())

        # Call the webtest method
        predictions = webtest(["T0", "T1"], zip_path="test_model.zip")

        # Assert that the output is a pandas DataFrame
        self.assertIsInstance(predictions, pd.DataFrame)

        # Assert that the DataFrame has the correct columns
        self.assertIn("predictions", predictions.columns)
        self.assertIn("training_data", predictions.columns)
        self.assertIn("test_data", predictions.columns)
        self.assertIn("technique_name", predictions.columns)

    def test_webtest_pickle(self):
        # Create a dummy TechniqueInferenceEngine
        u = np.random.rand(10, 4)
        v = np.random.rand(20, 4)
        technique_ids = [f"T{i}" for i in range(20)]
        hyperparameters = {
            "model_name": "wals",
            "c": 0.001,
            "regularization_coefficient": 0.00001,
        }
        model_name = hyperparameters.get("model_name", "wals")
        model_class, prediction_method, _ = (
            WalsRecommender,
            PredictionMethod.DOT,
            {},
        )
        model = model_class(m=u.shape[0], n=v.shape[0], k=u.shape[1])
        model._U = u
        model._V = v
        dummy_matrix = ReportTechniqueMatrix(
            indices=((0, 0),),
            values=(1,),
            report_ids=["dummy_report"],
            technique_ids=technique_ids,
        )
        tie = TechniqueInferenceEngine(
            training_data=dummy_matrix,
            validation_data=dummy_matrix,
            test_data=dummy_matrix,
            model=model,
            prediction_method=prediction_method,
            enterprise_attack_filepath="data/stix/enterprise-attack.json",
            hyperparameters=hyperparameters,
        )

        # Pickle the dummy engine
        with open("test_model.pkl", "wb") as f:
            pickle.dump(tie, f)

        # Call the webtest_pickle method
        predictions = webtest_pickle(["T0", "T1"], "test_model.pkl")

        # Assert that the output is a pandas DataFrame
        self.assertIsInstance(predictions, pd.DataFrame)

        # Assert that the DataFrame has the correct columns
        self.assertIn("predictions", predictions.columns)
        self.assertIn("training_data", predictions.columns)
        self.assertIn("test_data", predictions.columns)
        self.assertIn("technique_name", predictions.columns)

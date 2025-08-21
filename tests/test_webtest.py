import io
import zipfile
import unittest
import numpy as np
import pandas as pd

from tie.webtest import webtest, load_model_from_zip


class TestWebtest(unittest.TestCase):
    def test_webtest(self):
        # Create dummy data
        u = np.random.rand(10, 4)
        v = np.random.rand(20, 4)
        technique_ids = [f"T{i}" for i in range(20)]
        hyperparameters = {"model_name": "wals"}

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

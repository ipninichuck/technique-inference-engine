import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd

from tie.application import (
    predict_techniques,
    train_model,
    tune_hyperparameters,
)

app = FastAPI()

# Predict endpoint
class PredictRequest(BaseModel):
    model_path: str
    techniques: List[str]

@app.post("/predict")
def predict(request: PredictRequest):
    """
    Predicts techniques for a given report using a pickled model.
    """
    with open(request.model_path, "rb") as f:
        tie = pickle.load(f)
    predictions = predict_techniques(tie, request.techniques)
    return predictions.to_dict()

# Train endpoint
class TrainRequest(BaseModel):
    model: str
    dataset: str
    attack: str
    outfile: str
    validation_ratio: float = 0.1
    test_ratio: float = 0.2

@app.post("/train")
def train(request: TrainRequest):
    """
    Trains a model.
    """
    tie = train_model(
        request.model,
        request.dataset,
        request.attack,
        request.validation_ratio,
        request.test_ratio,
    )
    with open(request.outfile, "wb") as f:
        pickle.dump(tie, f)
    return {"message": f"Model trained and saved to {request.outfile}"}

# Tune endpoint
class TuneRequest(BaseModel):
    model: str
    dataset: str
    attack: str
    validation_ratio: float = 0.1
    test_ratio: float = 0.2

@app.post("/tune")
def tune(request: TuneRequest):
    """
    Tunes hyperparameters for a model.
    """
    best_hyperparameters = tune_hyperparameters(
        request.model,
        request.dataset,
        request.attack,
        request.validation_ratio,
        request.test_ratio,
    )
    return {"best_hyperparameters": best_hyperparameters}

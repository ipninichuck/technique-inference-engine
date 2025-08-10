import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set

# Add src to path to be able to import tie
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tie.matrix_builder import ReportTechniqueMatrixBuilder
from tie.engine import TechniqueInferenceEngine
from tie.constants import PredictionMethod
from tie.recommender import (
    WalsRecommender,
    BPRRecommender,
    FactorizationRecommender,
    TopItemsRecommender,
    ImplicitBPRRecommender,
    ImplicitWalsRecommender,
)

app = FastAPI(
    title="Technique Inference Engine API",
    description="A REST API for the Technique Inference Engine.",
    version="1.0.0"
)

# In-memory storage for data and models
state: Dict[str, Any] = {
    "training_data": None,
    "test_data": None,
    "validation_data": None,
    "data_builder": None,
    "trained_models": {},
}

# --- Pydantic Models ---

class PrepareDataParams(BaseModel):
    validation_ratio: float = 0.1
    test_ratio: float = 0.2
    dataset_filepath: str = "data/combined_dataset_full_frequency.json"
    enterprise_attack_filepath: str = "data/stix/enterprise-attack.json"

class PrepareDataResponse(BaseModel):
    message: str
    num_training_interactions: int
    num_test_interactions: int
    num_validation_interactions: int

class TrainParams(BaseModel):
    embedding_dimension: int = 4
 feat/containerize-tie-api
    hyperparameters: Dict[str, Any] = Field(..., example={"epochs": 25, "regularization_coefficient": 0.01})


class TrainResponse(BaseModel):
    message: str
    model_name: str
    mse: Optional[float] = None
    best_hyperparameters: Optional[Dict[str, Any]] = None

class PredictParams(BaseModel):
    techniques: Set[str] = Field(..., example={"T1059.003", "T1071.001"})
    hyperparameters: Optional[Dict[str, Any]] = None

class PredictResponse(BaseModel):
    predictions: List[Dict[str, Any]]

# --- Helper Functions ---

def get_recommender_class(model_name: str):
    model_map = {
        "wals": WalsRecommender,
        "bpr": BPRRecommender,
        "factorization": FactorizationRecommender,
        "top_items": TopItemsRecommender,
        "implicit_bpr": ImplicitBPRRecommender,
        "implicit_wals": ImplicitWalsRecommender,
    }
    if model_name not in model_map:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    return model_map[model_name]

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Technique Inference Engine API"}

@app.post("/prepare-data", response_model=PrepareDataResponse)
def prepare_data(params: PrepareDataParams):
    """
    Load and prepare the dataset for training, validation, and testing.
    """
    try:
        data_builder = ReportTechniqueMatrixBuilder(
            combined_dataset_filepath=params.dataset_filepath,
            enterprise_attack_filepath=params.enterprise_attack_filepath,
        )
        training_data, test_data, validation_data = data_builder.build_train_test_validation(
            params.test_ratio, params.validation_ratio
        )

        state["data_builder"] = data_builder
        state["training_data"] = training_data
        state["test_data"] = test_data
        state["validation_data"] = validation_data

        return {
            "message": "Data prepared successfully.",
            "num_training_interactions": training_data.to_numpy().sum(),
            "num_test_interactions": test_data.to_numpy().sum(),
            "num_validation_interactions": validation_data.to_numpy().sum(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train/{model_name}", response_model=TrainResponse)
def train_model(model_name: str, params: TrainParams):
    """
    Train a specified recommender model.
    """
    if state["training_data"] is None:
        raise HTTPException(status_code=400, detail="Data not prepared. Please call /prepare-data first.")

    training_data = state["training_data"]
    validation_data = state["validation_data"]
    test_data = state["test_data"]

    model_class = get_recommender_class(model_name)

    model = model_class(
        m=training_data.m,
        n=training_data.n,
        k=params.embedding_dimension,
    )

    tie_engine = TechniqueInferenceEngine(
        training_data=training_data,
        validation_data=validation_data,
        test_data=test_data,
        model=model,
        prediction_method=PredictionMethod.DOT, # Defaulting to DOT, can be parameterized
        enterprise_attack_filepath=state["data_builder"].enterprise_attack_filepath,
    )

    try:
        mse = tie_engine.fit(**params.hyperparameters)
        state["trained_models"][model_name] = (tie_engine, params.hyperparameters)

        return {
            "message": f"Model '{model_name}' trained successfully.",
            "model_name": model_name,
            "mse": mse,
 feat/containerize-tie-api
            "best_hyperparameters": params.hyperparameters,

        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during model training: {e}")


@app.post("/predict/{model_name}", response_model=PredictResponse)
def predict_techniques(model_name: str, params: PredictParams):
    """
    Predict techniques for a new report using a trained model.
    """
    if model_name not in state["trained_models"]:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' is not trained. Please train it first.")

    tie_engine, hyperparameters = state["trained_models"][model_name]

    # Use provided hyperparameters for prediction if available, otherwise use trained ones
    pred_hyperparams = params.hyperparameters if params.hyperparameters is not None else hyperparameters

    try:
        predictions_df = tie_engine.predict_for_new_report(params.techniques, **pred_hyperparams)
        predictions = predictions_df.reset_index().rename(columns={'index': 'technique_id'}).to_dict(orient='records')
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

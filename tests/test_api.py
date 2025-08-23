import os
import pickle
from tie.api import train, predict, tune, TrainRequest, PredictRequest, TuneRequest

def test_train_predict_tune():
    # Define file paths
    dataset_path = "data/combined_dataset_full_frequency.json"
    attack_path = "data/stix/enterprise-attack.json"
    model_path = "test_model_api.pkl"

    # Test training
    train_request = TrainRequest(
        model="wals",
        dataset=dataset_path,
        attack=attack_path,
        outfile=model_path,
    )
    response = train(train_request)
    assert response == {"message": f"Model trained and saved to {model_path}"}
    assert os.path.exists(model_path)

    # Test prediction
    predict_request = PredictRequest(
        model_path=model_path,
        techniques=["T1566.001", "T1078"],
    )
    predictions = predict(predict_request)
    assert "predictions" in predictions
    assert "training_data" in predictions

    # Test tuning
    tune_request = TuneRequest(
        model="wals",
        dataset=dataset_path,
        attack=attack_path,
    )
    response = tune(tune_request)
    assert "best_hyperparameters" in response

    # Clean up the created model file
    os.remove(model_path)

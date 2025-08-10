# Technique Inference Engine API

This document provides instructions and documentation for the containerized REST API for the Technique Inference Engine (TIE).

## Overview

The Technique Inference Engine (TIE) is a machine learning application that predicts likely MITRE ATT&CK techniques based on an initial set of observed techniques. This containerized application exposes the core functionalities of TIE through a RESTful API, allowing for easy integration and use without needing to manage the underlying Python environment.

The API provides endpoints to:
- Prepare the dataset for training and evaluation.
- Train various recommender models.
- Predict new techniques based on a given set of techniques.

## Getting Started

To get started with the TIE API, you need to have Docker installed on your system.

### Building the Docker Image

Navigate to the root directory of this project and run the following command to build the Docker image:

```bash
docker build -t tie-api .
```

### Running the Docker Container

Once the image is built, you can run it as a container with the following command:

```bash
docker run -p 8000:8000 tie-api
```

The API will be accessible at `http://localhost:8000`.

## API Endpoints

The API is documented using Swagger UI, which is available at `http://localhost:8000/docs` when the container is running.

### Health Check

- **GET /**: Returns a welcome message to confirm the API is running.

### Data Preparation

- **POST /prepare-data**: Loads and prepares the dataset for training, validation, and testing.

  **Request Body:**
  ```json
  {
    "validation_ratio": 0.1,
    "test_ratio": 0.2,
    "dataset_filepath": "data/combined_dataset_full_frequency.json",
    "enterprise_attack_filepath": "data/stix/enterprise-attack.json"
  }
  ```

  **Response:**
  ```json
  {
    "message": "Data prepared successfully.",
    "num_training_interactions": 1234,
    "num_test_interactions": 234,
    "num_validation_interactions": 123
  }
  ```

### Model Training

- **POST /train/{model_name}**: Trains a specified recommender model.
  - `model_name` can be one of: `wals`, `bpr`, `factorization`, `top_items`, `implicit_bpr`, `implicit_wals`.

  **Request Body:**
  The request body requires an `embedding_dimension` and a `hyperparameters` dictionary containing the parameters for the specific model being trained.

  **Example for `wals` model:**
  ```json
  {
    "embedding_dimension": 4,
    "hyperparameters": {
      "epochs": 25,
      "regularization_coefficient": 0.00001,
      "c": 0.001
    }
  }
  ```

  **Example for `bpr` model:**
  ```json
  {
    "embedding_dimension": 4,
    "hyperparameters": {
      "epochs": 20,
      "learning_rate": 0.001,
      "regularization": 0.01
    }
  }
  ```

  **Response:**
  ```json
  {
    "message": "Model 'wals' trained successfully.",
    "model_name": "wals",
    "mse": 0.809,
    "best_hyperparameters": {
      "epochs": 25,
      "regularization_coefficient": 0.00001,
      "c": 0.001
    }
  }
  ```

### Prediction

- **POST /predict/{model_name}**: Predicts techniques for a new report using a trained model.

  **Request Body:**
  ```json
  {
    "techniques": [
      "T1059.003",
      "T1071.001"
    ],
    "hyperparameters": null
  }
  ```

  **Response:**
  ```json
  {
    "predictions": [
      {
        "technique_id": "T1484.002",
        "predictions": 0.000080,
        "training_data": 0.0,
        "test_data": 0.0,
        "technique_name": "Domain Trust Modification"
      }
    ]
  }
  ```
---
*Copyright © 2024 MITRE Engenuity. Approved for public release. Document number(s) CT0124.*

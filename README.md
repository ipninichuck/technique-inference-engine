# Technique Inference Engine

The Technique Inference Engine (TIE) is a standalone Python application that allows
cyber defenders to forecast an adversary's next steps by predicting associated
[MITRE ATT&CK](https://attack.mitre.org/) techniques from previously observed
techniques. TIE enables defenders to build a complete picture of an adversary and
their actions.

This project is created and maintained by the [MITRE Center for Threat-Informed
Defense](https://ctid.mitre.org/) in furtherance of our mission to advance the
start of the art and the state of the practice in threat-informed defense
globally. The project is funded by our research participants.

**Table Of Contents:**

- [Getting Started](#getting-started)
- [Usage](#usage)
- [Getting Involved](#getting-involved)
- [Questions and Feedback](#questions-and-feedback)
- [Notice](#notice)

## Getting Started

To get started with the Technique Inference Engine, you will need to have Python 3.10+
and [Poetry](https://python-poetry.org/) installed.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/center-for-threat-informed-defense/technique-inference-engine.git
    cd technique-inference-engine
    ```

2.  **Install the dependencies:**

    ```bash
    poetry install
    ```

## Usage

The Technique Inference Engine provides a command-line interface (CLI) for training
models, making predictions, and tuning hyperparameters.

### Training a Model

To train a model, use the `train` command:

```bash
poetry run tie train --model <model_name> --dataset <path_to_dataset> --attack <path_to_attack_stix> --outfile <path_to_save_model>
```

-   `<model_name>`: The name of the model to train (e.g., `wals`, `bpr`).
-   `<path_to_dataset>`: Path to the dataset file (e.g., `data/combined_dataset_full_frequency.json`).
-   `<path_to_attack_stix>`: Path to the enterprise attack STIX file (e.g., `data/stix/enterprise-attack.json`).
-   `<path_to_save_model>`: Path to save the trained model file.

### Making Predictions

To make predictions with a trained model, use the `predict` command:

```bash
poetry run tie predict --model <path_to_trained_model> --techniques <technique_id_1> <technique_id_2> ...
```

-   `<path_to_trained_model>`: Path to the trained model file.
-   `<technique_id_1> <technique_id_2> ...`: A list of technique IDs.

### Tuning Hyperparameters

To tune the hyperparameters for a model, use the `tune` command:

```bash
poetry run tie tune --model <model_name> --dataset <path_to_dataset> --attack <path_to_attack_stix>
```

-   `<model_name>`: The name of the model to tune (e.g., `wals`, `bpr`).
-   `<path_to_dataset>`: Path to the dataset file.
-   `<path_to_attack_stix>`: Path to the enterprise attack STIX file.

## Getting Involved

There are several ways that you can get involved with this project and help
advance threat-informed defense:

-   **Train your own Engine.** Train the Technique Inference Engine on your own CTI
    data using the CLI.
-   **Contribute your own CTI.** We are interested in further expanding the
    Engine's dataset. If you have your own CTI you'd like to share, we would
    welcome your contribution.

## Questions and Feedback

We welcome your feedback and contributions to help advance Technique Inference
Engine. Please see the guidance for contributors if are you interested in
[contributing or simply reporting issues.](/CONTRIBUTING.md)

Please submit
[issues](https://github.com/center-for-threat-informed-defense/technique-inference-engine/issues)
for any technical questions/concerns or contact
[ctid@mitre.org](mailto:ctid@mitre.org?subject=subject=Question%20about%20technique-inference-engine)
directly for more general inquiries.

## Notice

Copyright 2024 MITRE. Approved for public release. Document number CT0124.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

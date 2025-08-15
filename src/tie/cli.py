import argparse
import pickle

from tie.application import (
    predict_techniques,
    train_model,
    tune_hyperparameters,
)


def main():
    parser = argparse.ArgumentParser(
        prog="TechniqueInferenceEngine",
        description="A command-line interface for the Technique Inference Engine.",
        epilog="For further help and support, please reach out to CTID.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a model.")
    train_parser.add_argument("--model", required=True, help="The model to train.")
    train_parser.add_argument("--dataset", required=True, help="Path to the dataset file.")
    train_parser.add_argument(
        "--attack", required=True, help="Path to the enterprise attack STIX file."
    )
    train_parser.add_argument("--outfile", required=True, help="Path to save the trained model.")
    train_parser.add_argument("--validation-ratio", type=float, default=0.1)
    train_parser.add_argument("--test-ratio", type=float, default=0.2)

    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Make predictions with a trained model.")
    predict_parser.add_argument("--model", required=True, help="Path to the trained model.")
    predict_parser.add_argument(
        "--techniques", required=True, nargs="+", help="A list of technique IDs."
    )

    # Tune command
    tune_parser = subparsers.add_parser("tune", help="Tune hyperparameters for a model.")
    tune_parser.add_argument("--model", required=True, help="The model to tune.")
    tune_parser.add_argument("--dataset", required=True, help="Path to the dataset file.")
    tune_parser.add_argument(
        "--attack", required=True, help="Path to the enterprise attack STIX file."
    )
    tune_parser.add_argument("--validation-ratio", type=float, default=0.1)
    tune_parser.add_argument("--test-ratio", type=float, default=0.2)

    args = parser.parse_args()

    if args.command == "train":
        tie = train_model(
            args.model,
            args.dataset,
            args.attack,
            args.validation_ratio,
            args.test_ratio,
        )
        with open(args.outfile, "wb") as f:
            pickle.dump(tie, f)
        print(f"Model trained and saved to {args.outfile}")
    elif args.command == "predict":
        with open(args.model, "rb") as f:
            tie = pickle.load(f)
        predictions = predict_techniques(tie, args.techniques)
        print(predictions)
    elif args.command == "tune":
        best_hyperparameters = tune_hyperparameters(
            args.model,
            args.dataset,
            args.attack,
            args.validation_ratio,
            args.test_ratio,
        )
        print("Best hyperparameters found:")
        print(best_hyperparameters)


if __name__ == "__main__":
    main()

"""Module for initializing nested MLFlow run."""
import argparse
from typing import Text

import mlflow
import yaml


def start_pipeline(config_path: Text, run_name: str) -> None:
    """Start a new MLflow run each time we launch the DVC pipeline.

       Print the MLFLOW_RUN_ID and save as an environment variable. 
       This allows the possibility to track nested runs for each stage
       of the pipeline.

    Args:
        config_path (Text): path to config
        run_name (str): specify run name
    """
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    mlflow.set_experiment(config['base']['project_experiment_name'])
    with mlflow.start_run(run_name=run_name):
        print(mlflow.active_run().info.run_id)

        mlflow.log_artifact('dvc.yaml')
        mlflow.log_artifact(config_path)


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args_parser.add_argument('--run_name', dest='run_name', required=True)
    args = args_parser.parse_args()

    start_pipeline(config_path=args.config, run_name=args.run_name)

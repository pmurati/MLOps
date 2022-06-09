from typing import Text
import yaml
import os
import argparse
import mlflow


def start_pipeline(config_path: Text, run_name: str)->None:
    """start a new MLflow run each time we launch the DVC pipeline.
    Args:
        config_path {Text}: path to config
    """

    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    mlflow.set_experiment(config['base']['project_experiment_name'])
    with mlflow.start_run(run_name=run_name):
        print(mlflow.active_run().info.run_id)
        #os.environ['MLFLOW_RUN_ID'] = mlflow.active_run().info.run_id
        #print(os.environ['MLFLOW_RUN_ID'])
        mlflow.log_artifact('dvc.yaml')
        mlflow.log_artifact(config_path)


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args_parser.add_argument('--run_name', dest='run_name', required=True)
    args = args_parser.parse_args()

    start_pipeline(config_path=args.config, run_name=args.run_name)

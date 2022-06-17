"""Module for creating the MLFlow nested run decorator."""
from functools import wraps
from typing import Callable

import mlflow
import yaml


def mlflow_run(wrapped_function: Callable) -> Callable:
    """Decorator to turn every stage into MLflow nested run.

    Args:
        wrapped_function (Callable): the respective function in each stage

    Returns:
        wrapped function (Callable): the input function, tracked under the respective MLFLOW_RUN_ID
    """
    config_path = 'params.yaml'
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    @wraps(wrapped_function)
    def wrapper(*args, **kwargs):
        mlflow.set_experiment(config['base']['project_experiment_name'])
        # recover parent run thanks to MLFLOW_RUN_ID env variable
        with mlflow.start_run():
            # start child run
            with mlflow.start_run(run_name=wrapped_function.__name__, nested=True):
                return wrapped_function(*args, **kwargs)
    return wrapper

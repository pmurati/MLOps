from functools import wraps
from typing import Text
import yaml

import mlflow


def mlflow_run(wrapped_function):
    '''Decorator to turn every stage into MLflow nested run.
    '''

    config_path = 'params.yaml'
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    @wraps(wrapped_function)
    def wrapper(*args, **kwargs):
        mlflow.set_experiment(config['base']['project_experiment_name'])
        with mlflow.start_run():  # recover parent run thanks to MLFLOW_RUN_ID env variable
            with mlflow.start_run(run_name=wrapped_function.__name__, nested=True):  # start child run
                return wrapped_function(*args, **kwargs)
    return wrapper

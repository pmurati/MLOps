"""Module for the training stage."""
import argparse
from typing import Text

import joblib
import mlflow
import pandas as pd
import yaml

from src.train.train import train
from src.utils.logs import get_logger
from src.utils.mlflow_run_decorator import mlflow_run


@mlflow_run
def train_model(config_path: Text) -> None:
    """Train model.

       Train the model on the train set. Get the path to the data and the
       parametrization for the model used from the config.

       This stage uses a helper function that does a GridSearchCV,
       with the intend of further modularization and higher flexibility of
       this script. 

       The best model is saved to the models directory as a joblib file.
       In addition, the model is logged via mlflow. 

    Args:
        config_path (Text): path to config
    """
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    logger = get_logger('TRAIN', log_level=config['base']['log_level'])

    logger.info('Get estimator name')
    estimator_name = config['train']['estimator_name']
    logger.info(f'Estimator: {estimator_name}')

    logger.info('Load train dataset')
    train_df = pd.read_csv(config['data_split']['trainset_path'])

    logger.info('Train model')
    model = train(
        df=train_df,
        target_column=config['featurize']['target_column'],
        estimator_name=estimator_name,
        param_grid=config['train']['estimators'][estimator_name]['param_grid'],
        cv=config['train']['cv']
    )
    logger.info(f'Best score: {model.best_score_}')

    logger.info('Save model')
    models_path = config['train']['model_path']
    joblib.dump(model, models_path)

    mlflow.log_param('chosen_estimator', model.best_estimator_)
    mlflow.log_param('parametrization', model.best_params_)
    mlflow.log_metric('F1', model.best_score_)

    mlflow.sklearn.log_model(model, 'model')


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    train_model(config_path=args.config)

"""Module for featurization stage of raw data sets."""
import argparse
from typing import Text

import mlflow
import pandas as pd
import yaml

from src.utils.logs import get_logger
from src.utils.mlflow_run_decorator import mlflow_run


@mlflow_run
def featurize(config_path: Text) -> None:
    """Create new features and save the processed dataset.

    Args:
        config_path (Text): path to config
    """
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    logger = get_logger('FEATURIZE', log_level=config['base']['log_level'])

    logger.info('Load raw data')
    dataset = pd.read_csv(config['data_load']['dataset_csv'])

    logger.info('Extract features')
    dataset['sepal_length_to_sepal_width'] = dataset['sepal_length'] / \
        dataset['sepal_width']
    dataset['petal_length_to_petal_width'] = dataset['petal_length'] / \
        dataset['petal_width']
    featured_dataset = dataset[[
        'sepal_length', 'sepal_width', 'petal_length', 'petal_width',
        'sepal_length_to_sepal_width', 'petal_length_to_petal_width',
        'target'
    ]]

    logger.info('Save features')
    features_path = config['featurize']['features_path']
    featured_dataset.to_csv(features_path, index=False)

    mlflow.log_param('features', featured_dataset.columns)


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    featurize(config_path=args.config)

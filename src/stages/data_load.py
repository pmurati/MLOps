"""Module for the data loading stage."""
import argparse
from typing import Text

import dvc.api
import mlflow
import pandas as pd
import yaml
from sklearn.datasets import load_iris

from src.utils.logs import get_logger
from src.utils.mlflow_run_decorator import mlflow_run


@mlflow_run
def data_load(config_path: Text) -> None:
    """Load raw data.

       Depending on the parameter revision_on (taken from config),
       a specific version of data is loaded from the DVC repo.
       Othewise, the iris dataset is loaded from sklearn.datasets.

    Args:
        config_path (Text): path to config
    """
    with open(config_path) as conf_file:
        config = yaml.safe_load(conf_file)

    logger = get_logger('DATA_LOAD', log_level=config['base']['log_level'])
    logger.info('Get dataset')

    if config['data_load']['revision_on']:

        logger.info('Grab dataset version {}'.format(
            config['data_load']['version']))
        data_url = dvc.api.get_url(
            path=config['data_load']['dataset_csv'],
            repo=config['data_load']['repo'],
            rev=config['data_load']['version']
        )
        dataset = pd.read_csv(data_url, sep=',')

        # log data url and version tag in mlflow
        mlflow.log_param('data_url', data_url)
        mlflow.log_param('version', config['data_load']['version'])
    else:
        data = load_iris(as_frame=True)

        dataset = data.frame
        dataset.rename(
            columns=lambda colname: colname.strip(' (cm)').replace(' ', '_'),
            inplace=True
        )

    logger.info('Save raw data')
    dataset.to_csv(config['data_load']['dataset_csv'], index=False)

    mlflow.log_param('input_rows', dataset.shape[0])
    mlflow.log_param('input_cols', dataset.shape[1])


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    data_load(config_path=args.config)

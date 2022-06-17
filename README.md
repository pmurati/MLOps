# MLOps Demo

This repository demosntrates a composite framework for data pipeline and version orchestration as well tracking and model comparison, using a combination of tools like git, DVC and MLFlow.

# Table of Contents

- [MLOps Demo](#mlops-demo)
- [Table of Contents](#table-of-contents)
- [File Descriptions](#file-descriptions)
- [Technologies Used](#technologies-used)
- [Executive Summary](#executive-summary)
  - [Goal](#goal)
  - [DVC](#dvc)
  - [MLFlow](#mlflow)
  - [A combined approach](#a-combined-approach)
  - [Setup](#setup)
  - [Initializing and updating pipeline](#initializing-and-updating-pipeline)
  - [Evaluation with MLFlow Tracking](#evaluation-with-mlflow-tracking)
  - [Future Development](#future-development)

# File Descriptions

<p>
<details>
<summary>Show/Hide</summary></br>

- [.dvc](/.dvc/) : created directory at DVC initialization, containing congifuration, default cache location and other internal files and directories  
- [data](/data/) : contains the **raw/** and **processed/** sub directories for raw data (coming from the first pipeline stage data load) and for processed data (comming from pipeline stages for featurization and for splitting into train and test data) respectively; DVC automatically creates a .gitignore for all data sets
- [docs](/docs/) : contains markdown files, used by MkDocs in the creation of html documentation for the source code
- [images](/images/) : images used in this README
- [models](/models/) : contains **model.joblib** file (output from the training stage); DVC automatically creates a .gotignore file for the model
- [reports](/reports/) : contains the **metrics.json** with the resulting metrics and confusion matrix plot **confusion_matrix.png** on the test set (output from evaluation stage)
- [site](/site/) : MkDocs documentation
- [src](/src/) : contains the source code
  - [report](src/report/) : folder containing **visualizing.py** for creation of confusion matrix plot 
  - [stages](/src/stages/) : folder containg the different python functions associated with the different stages in the pipeline, namely **data_load.py** for loading the data, **featurize.py** for feature engineering, **data_split.py** for splitting the data into train and test sets, **train.py** for training the model on the train set and **evaluate.py** for evaluating the trained model on the test set  
  - [train](/src/train/) : folder containing the python script **train.py** with explicit model that is loaded into its associated stage; the intention is to add more models in the future and thus increase modularization of this project
  - [utils](/src/utils/) : folder containg helper functions, namely **logs.py** for logging functionalities, **start_pipeline.py** for initialization of a nested MLFlow run and **mlflow_run_decorator.py** that creates the associated MLFLow nested run decorator for each stage of the pipeline  
- [.dvcignore](/.dvcignore) : files and folders excluded from DVC version control
- [dvc.lock](/dvc.lock) : contains the md5 hashes of input and output data from the pipeline; links to the different data versions in the (remote) data storage
- [dvc.yaml](/dvc.yaml) : yaml file for specification of different stages, inputs, outputs and dependencies of pipeline
- [Makefile](/Makefile) : contains make commands for
  -  dependencies installation
  -  coding standards
  -  DVC & MLFlow Pipeline
- [mkdocs.yaml](/mkdocs.yaml) : config file for doc site generator
- [params.yaml](/params.yaml) : config file, used throughout the source code
- [requirements-dev.txt](/requirements-dev.txt) : dependencies for pipeline, including python pacakges for testing, linting and documentation 
- [requirements.txt](/requirements.txt) : dependencies for pipeline

</details>
</p>

# Technologies Used

<p>
<details>
<summary>Show/Hide</summary></br>

The user should be proficient with python programming, especially with the most common data science libraries: pandas, sklearn, matplotlib, to name a few. The user should be familiar with joblib, yaml and json files. In order to understand the functioning of the two tools presented in this demo, namely DVC and MLFlow, it is necessary to have some knowledge about git version control. Finally, being familiar with makefiles will come in handy for using this repo's make commands.

</details>
</p>

<p>
<details>
<summary>Show/Hide</summary></br>
Details
</details>
</p>

# Executive Summary

## Goal

<p>
<details>
<summary>Show/Hide</summary></br>

![MLOps Overview](/images/MLOps_Overview.png "taken from J Garg - Real Time Learning Course on MLOps Fundamentals")

The picture above captures the key differences between the two phases of ML projects: the experimentation and development phase on the one side and staging and production on the other. Typically, Data Scientists are concerned with experimentation/development of ML models. However, no matter how good the model, no value is generated unless the model can be put into production and mantained in an efficient manner. In contrast to traditional software engineering projects, machine learning projects require additional care with respect to DevOps tasks. 

The goal of this repository is to focus on one of those tasks, namely the pipeline for (re-)training a model, as well as versioning of the code and machine learning specific artifacts like the model itself, the data used and resulting metrics (see the part of the graphic in staging/production under automated pipeline and ML metadata store). This is an important step in creating code reproducibility, sharing models and data with collaborators, comparing performance among different parametrizations of models and delivering consistency in the overall ML lifecycle.       

The graphic was taken from J Garg - Real Time learning's course on [MLOps Fundamentals](https://www.udemy.com/course/mlops-course/). For more information on the basics of MLOps, its benefits, importance and implementation, I refer to this course for a high-level introduction.

</details>
</p>

## DVC

<p>
<details>
<summary>Show/Hide</summary></br>

In analogy to git, DVC is a data version control, with similar commands and executables to git. In essence, it allows for the (remote) storage of large data files and their versioning, which is not recommended to be dealt with by git. Once a data file is added to DVC, a .dvc metafile is created at the same location as the original, as well as an additional .gitignore file. Instead of the large original, git will deal with the new and fairly small metafile which contains information about the path to the original as well as changes to that file in the form of an md5 hash. Now, to checkout a different version of the data, git will load the respective version of the metafile, which in turn points to the DVC storage.

>**NOTE:** A data file can be anything from raw or processed input data for ML models, the created model file itself, as well as output metrics or plotted files. Although we will use DVC mainly for input model data in this demo, its should be noted that DVC's functionality extends to a broader spectrum of files.

The above procedure is summarized in the following graphic, taken from the course [Iterative Tools for Data Scientists & Analysts](https://learn.iterative.ai/).

![DVC data versioning](/images/DVC_data_versioning.png "taken from iterative.ai - Iterative Tools for Data Scientists & Analysts")

That being said, DVC also allows for the orchestration of data pipelines. Given a configuration file named [dvc.yaml](/dvc.yaml), DVC will build the respective DAG (directed acyclic graph) and execute it, given a set of dependencies (**what** is the input data and **which** python scripts should be executed?), cmd commands (**how** should the python script be executed?), parameters (a reference to variables from a [params.yaml](/params.yaml) config file) and outputs (**what** is the generated output?) that need to be defined for each stage of the pipeline.

Setting up a pipeline this way not only automates the whole data science process from data extraction to model evaluation, DVC will also track versions of all input and output files automatically and stores them in a [dvc.lock](/dvc.lock) file which is created and/or updated at runtime. This .lock file is similar to the structure of the .yaml file: it is logically structured in accordance to the stages in the pipeline with the added information from the single metafiles described above (i.e. path information and a md5 hash recording the changes per data file). Tu build and run the pipeline, use the CLI command

```bash
dvc repro
```
>**NOTE:** When executed multiple times, DVC will run only those stages in which it detects changes, in order to increase performance. Add a force flag to the command to execute all stages nonetheless.

In this project, the following pipeline is implemented, based on the one from the course [Iterative Tools for Data Scientists & Analysts](https://learn.iterative.ai/).

![DVC data pipeline](/images/DVC_data_pipeline.png "taken from iterative.ai - Iterative Tools for Data Scientists & Analysts")

Each pipeline module corresponds to a python script, properly set up to receive input from `params.yaml` at runtime. Data is loaded and passed to the first stage (in our demo, it is actually generated from the sklearn iris data set) and throughout the pipeline, additional processed data is generated. In the end, a model, metrics, visualizations etc. are created and returned. 

</details>
</p>

## MLFlow

<p>
<details>
<summary>Show/Hide</summary></br>

MLFlow is a similar tool to DVC in that it also keeps track of ML model results. It allows the exact replication of model training and thus, functions as a tool for collaboartion and model sharing across multiple members of a data science team. However, it is best suited for comparing different models based on user defined criteria such as: data used, model (hyper)parameters and result metrics. Moreover, MLFlow offers a diverse range of deployment options for the created models. In this demo, the focus will lie on its model tracking functionalities.
>For that, MLFlow allows the setup of a remote tracking server that can be accessed by the users. In this demo however, the results will be saved locally and results can be viewed by running a local server.

MLFlow tracks models by using the logical framework of an experiment. This can be, but is not restricted to, a specific ML model in which one wants to compare different parametrizations. To each experiment, we can assign runs. Each trained model with its unique parametrization yields a single run and different runs within an experiment can be compared with one another.

What constitutes a parametrization? As already mentioned, this can be the data used (although, as we will see in the next sub section, this will be handled in a more efficient way by combining DVC with MLFlow functionalities), the model parameters, the evaluation metrics for training and testing, plots that have been generated, or the model itself (which can be saved in a way that deployment is simplified). However, even config files like the [params.yaml](/params.yaml) or [dvc.lock](/dvc.lock) files can be stored as artifacts with MLFlow. In the end, it is up to the user to decide what is considered to be important.

To set up an experiment, it suffices to add the following line of code to a python script

```bash
mlflow.set_experiment("experiment name")
```

followed by 

```bash
with mlflow.start_run("run name"):
  ...
```
to instanciate a MLFLow run. Within this with statement, one can use MLFLow's logging functionalities that take the form of

```bash
mlflow.log_param("parameter name", parameter)
mlflow.log_metric("metric name", metric)
mlflow.log_model(model,"model name")
mlflow.log_artifact(artifact)
```

To start the local tracking UI, run the CLI command

```
mlflow ui
```

For more information see the official [MLFlow docs](https://www.mlflow.org/docs/latest/quickstart.html) and clone the github repo for a series of [examples](https://github.com/mlflow/mlflow/tree/master/examples)

</details>
</p>

## A combined approach

<p>
<details>
<summary>Show/Hide</summary></br>

DVc and MLFlow have some overlapping features as showcased in the previous sections. This demo will explore the combination of
- git for code version control
- DVC for data version control and pipeline orchestration
- MLFlow for tracking/comparing runs and experiments (as well as deployment, see the section on [Future Deployment](#future-development))
The intend of this project is to demonstrate one route of what is generally possible when combining different functionalities, as described in the following. 

An MLFLow experiment and a dedicated run can be setup on top of the data pipeline. They just have to be initialized before the first stage is triggered. With that, one is able to log whatever is considered to be necessary in the respective stage. Additionally, MLFLow has the option to create nested runs. For comparison and a better overview of the same stage in different runs, it might be useful to have parameters, artifacts, etc. associated with the stage they are coming from (this is a design choice, again for the sake of demonstrating the possibilities of these tools). 

In the initialization step, the `MLFLOW_RUN_ID` is saved as an environmental variable. By setting an appropriate decorator function on top of each stage, each part of the pipeline gets associated with the same run (by making use of `MLFLOW_RUN_ID`). Please refer to the code documentation [...]. For a more detailed explanation, see [Track DVC Pipeline Runs with MLFlow](https://www.sicara.fr/blog-technique/dvc-pipeline-runs-mlflow).

Another hybrid use is the exploitation of DVC's strong alignment with git commands. Using the tagging functionality of git, we can assign different versions to our data (or better to our metadatafile `dvc.lock`, more on that in the next section). Then, by using the python dvc api, it is possible to specify the version tag and with that get the desired data into the particular stage of the pipeline. Now, MLFlow can just log the version tag as a parameter, instead of the whole data (which DVC takes care of). 

The code will look something like this

```bash
data_url = dvc.api.get_url(path="path to dataset",
            repo="path to repository",
            rev="version tag"
        )
dataset = pd.read_csv(data_url, sep=',')

# log data url and version tag in mlflow
mlflow.log_param('data_url', data_url)
mlflow.log_param('version', "version tag")
```

For more information on data versioning with DVc and MLFlow, see the video on [Data Versioning and Reproducible ML with DVC and MLFlow](https://databricks.com/fr/session_eu20/data-versioning-and-reproducible-ml-with-dvc-and-mlflow).

</details>
</p>

## Setup

<p>
<details>
<summary>Show/Hide</summary></br>

This section shows, how dvc is used in conjunction with git. First, initialize git and dvc with the following commands

```bash
git init
dvc init
git commit -m "initialize repo"
```

Two hidden folders are created. One for git and for DVC. Inside the .dvc folder lie some internal files and the config which will be altered next. By default, DVC recently started collecting anonymized usage analytics, so that the authors can better understand how their tool is used in order to improve it. It can be turned off by setting the analytics configuration option to false.

```bash
dvc config core.analytics false 
git commit .dvc/config -m "configure analytics options"
```

Next, to set a remote storage for DVC use

```bash
mkdir -p $(REMOTE_PATH)
dvc remote add -d dvc-remote $(REMOTE_PATH) -f
git commit .dvc/config -m "configure remote storage"
```

In this example, the remote storage is set locally ad referenced by the name dvc-remote. For a cloud storage, additional authentication steps might be required. DVC saves data in its cache. It might come in handy to set up a remote cache. This is done via

```bash
mkdir -p $(CACHE_PATH)
dvc cache dir $(CACHE_PATH)
git commit .dvc/config -m "configure remote cache"
```

The changes done through the above executions can be seen in the rspective [config file](/.dvc/config).

</details>
</p>

## Initializing and updating pipeline

<p>
<details>
<summary>Show/Hide</summary></br>

Assuming that a `dvc.yaml` file has been created, the one-liner 

```bash
dvc repro
```

suffices to run each step in the pipeline and save the data via DVC version control in the form of a `dvc.lock` file that is created during run time. DVC checks for changes in each stage and only updates the ones where it detects changes in the code (in the following the force flag -f is used to always perform each stage). 

In order to perform the composite DVC-MLFlow framework, we have to alter this command

```bash
MLFLOW_RUN_ID=`python ./src/utils/start_pipeline.py --config=params.yaml  --run_name=$(RUN_NAME)` \
	dvc repro -f
```
As mentioned in [this](#a-combined-approach) section, we have to specify an environment variable for the nested tracking logic to work. This is returned by the experiment- and run-initiation script [start_pipeline.py](/src/utils/start_pipeline.py), which takes the `params.yaml` file and a speecified run name as input. Given that, the pipeline is triggered. The pipeline will create .gitignore files for all dependency files and output data, as well as the .lock file. Both shall be added to git version control and commited to both git and DVC.

```bash
git add --all
git commit -m "Reproduce DVC pipeline"
dvc commit
```

Finally, to ensure that the data is versioned (such that MLFlow can save the tag as a parameter) we include a git tag und push the changes to DVC.

```bash
git tag -a $(TAG) -m "Some meaningful message"
dvc push
```

>Keep in mind that additional steps are needed such as `git push origin --tags`, when synchronizing with a remote git repo (origin).

</details>
</p>

## Evaluation with MLFlow Tracking

<p>
<details>
<summary>Show/Hide</summary></br>

The results of running the pipeline can be seen in the MLFLow UI, via

```bash
mlflow ui
```

![MLFlow UI](/images/MLFLow_UI.png)

Each row represents one run. There are distinct columns per tracked parameter and metric. Each run can be expanded to show all the nested runs, named after their stage. Different runs can be compared with respect to parameters and metrics and the logged models can be shared and made available for further usage. 

</details>
</p>

## Future Development

<p>
<details>
<summary>Show/Hide</summary></br>

To conclude, here is a list with further steps that build on the existing framework:

- setup a remote dvc cache/storage on cloud
- setup MLFlow tracking server
- include more model options, i.e. conceptualize a more modularized approach 
- test the practicality of nested mlflow runs
- integrate automated deployment of endpoints for the models (via MLFlow)
- include monitoring of model performance

</details>
</p>

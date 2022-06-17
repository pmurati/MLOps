CONFIG=params.yaml
RUN_NAME=DEMO_RUN
REMOTE_PATH=/tmp/MLOps-dvc-remote-storage
CACHE_PATH=/tmp/MLOPs-dvc-remote-cache
DATA_DIR=data/

PYTHON=python


help:
	@echo "Available Commands:"
	@echo "---------------------------------------------------------------------"
	@echo "Package Installation"
	@echo ""
	@echo "install          - Install package dependencies."
	@echo "dev_install      - Install package dependencies, including linting, formating and testing tools."
	@echo "---------------------------------------------------------------------"
	@echo "Coding Standards"
	@echo ""
	@echo "linting          - Apply isort, autopep8 and pydocstyle."
	@echo "---------------------------------------------------------------------"
	@echo "DVC & MLFlow Pipeline"
	@echo ""
	@echo "init             - Initialize git and dvc repository."
	@echo "analytics_off    - Disable DVC analytics data collection."
	@echo "set_remote       - Setup remote dvc repository."
	@echo "set_cache        - Setup remote dvc cache."
	@echo "init_remote      - Run commands: init, analytics_off, set_remote, set_cache."
	@echo "run_pipeline     - Start new MLFlow run each time the DVC pipeline is launched. Do code and data versioning and add tag for reference."
	@echo "run_pipeline_old - Older version of run_pipeline, without tagging."

install:
	python -m pip install --upgrade pip
	pip install --upgrade pip setuptools wheel 
	pip install -r requirements.txt

dev_install:
	python -m pip install --upgrade pip
	pip install --upgrade pip setuptools wheel
	pip install -r requirements-dev.txt

linting:
	isort src
	autopep8 --in-place --recursive src/
	pydocstyle --convention=google src/

init:
	git init
	dvc init 
	git commit -m "initialize repo"

#DVC has recently started collecting anonymized usage analytics so the authors
#can better understand how DVC is used. This helps them improve the tool.
#You can turn it off by setting the analytics configuration option to false.	
analytics_off:	
	dvc config core.analytics false 
	git commit .dvc/config -m "configure analytics options"

set_remote:
	mkdir -p $(REMOTE_PATH)
	dvc remote add -d dvc-remote $(REMOTE_PATH) -f
	git commit .dvc/config -m "configure remote storage"

set_cache:
	mkdir -p $(CACHE_PATH)
	dvc cache dir $(CACHE_PATH)
	git commit .dvc/config -m "configure remote cache"
#	dvc checkout --relink
#If you make a change to the cache.type, it doesn’t take effect immediately.
#You need to tell DVC to check out links instead of file copies	

init_remote:
	make init
	make analytics_off
	make set_remote	
	make set_cache


#MLFLOW_RUN_ID is not shared with dvc pipeline. Each line in a Makefile is a separate shell-process.
#So shell-export does not work for several processes: One way to do it is to put them into one line
#or line-break-escaped with '\'

#see this stackoverflow post:
#https://stackoverflow.com/questions/6995107/why-exported-variables-in-makefile-is-not-received-by-executable#6995160
run_pipeline:
	MLFLOW_RUN_ID=`$(PYTHON) ./src/utils/start_pipeline.py --config=$(CONFIG)$  --run_name=$(RUN_NAME)` \
	dvc repro -f 
	git add --all
	git commit -m "Reproduce DVC pipeline"
	dvc commit
#	git push --set-upstream origin name-of-branch
	git tag -a $(TAG) -m "Some meaningful message"
#	git push origin --tags
	dvc push

run_pipeline_old:
	MLFLOW_RUN_ID=`$(PYTHON) ./src/utils/start_pipeline.py --config=$(CONFIG)$  --run_name=$(RUN_NAME)` \
	dvc repro -f
	git add dvc.lock
	git commit -m "Reproduce DVC pipeline"
	dvc push

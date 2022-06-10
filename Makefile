CONFIG=params.yaml
RUN_NAME=DEMO_RUN
REMOTE_PATH=/tmp/MLOps-dvc-remote-storage
CACHE_PATH=/tmp/MLOPs-dvc-remote-cache
DATA_DIR=data/

PYTHON=python


help:
	@echo "Available Commands:"
	@echo "init 		- Initialize git and dvc repository."
	@echo "set_remote 	- Setup remote dvc repository."
	@echo "set_cache 	- Setup remote dvc cache."
	@echo "add_new		- Add new data file to dvc version control with version tag v1."
	@echo "add_modified - Add modified data file to dvc version control and specify the version tag."
	@echo "run_pipeline - Start new MLflow run each time the DVC pipeline is launched."

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

add_new:
	dvc add $(DATA)
	git add $(DATA_DIR).gitignore $(DATA).dvc
	git commit -m "$(DATA): track"
	git tag -a "v1" -m "raw data"
	dvc push
	git push --tags

add_modified:
	dvc commit $(DATA)
	git add $(DATA).dvc
	git commit -m "$(DATA): modified"
	git tag -a "v$(V)" -m "modified data"
	dvc push
	git push --tags

#MLFLOW_RUN_ID is not shared with dvc pipeline. Each line in a Makefile is a separate shell-process.
#So shell-export does not work for several processes: One way to do it is to put them into one line
#or line-break-escaped with '\'

#see this stackoverflow post:
#https://stackoverflow.com/questions/6995107/why-exported-variables-in-makefile-is-not-received-by-executable#6995160
run_pipeline:
	MLFLOW_RUN_ID=`$(PYTHON) ./src/utils/start_pipeline.py --config=$(CONFIG)$  --run_name=$(RUN_NAME)` \
	dvc repro -f
	git add dvc.lock
	git commit -m "Reproduce DVC pipeline"
	dvc push


run_test_pipeline:
	MLFLOW_RUN_ID=`$(PYTHON) ./src/utils/start_pipeline.py --config=$(CONFIG)$  --run_name=$(RUN_NAME)` \
	dvc repro -f 
	git add --all
	git commit -m "Reproduce DVC pipeline"
	dvc commit
#	git push --set-upstream origin name-of-branch
	git tag -a $(TAG) -m "Some meaningful message"
#	git push origin --tags
	dvc push

#Continue here !!!
#try to add this functionality: add version tag automatically when difference in inptut (raw) data
#is detected during first stage of the pipeline. Give the option in the params.yaml file to select
#different versions of data and save it as a parameter in mlflow
checkout:
	git checkout $(V) -- dvc.lock
	dvc checkout $(DATA)
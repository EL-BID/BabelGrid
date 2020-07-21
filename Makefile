.PHONY: create-env update-env

REPO=$(shell basename $(CURDIR))

create-env:
	python3 -m venv .$(REPO);
	source .$(REPO)/bin/activate; \
			pip3 install --upgrade -r requirements_dev.txt; \
			python3 -m ipykernel install --user --name=$(REPO);

update-env:
	source .$(REPO)/bin/activate; \
	pip3 install --upgrade -r requirements.txt;
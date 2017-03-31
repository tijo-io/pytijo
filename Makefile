.PHONY: all deps clean dev install test

help:
	@echo "  deps    - installs and configures dependencies in virtualenv"
	@echo "  clean   - removes unwanted files"
	@echo "  dev     - prepares a development environments"
	@echo "  install - install library on local system"
	@echo "  test    - run tox"

deps:
	pip install virtualenv
	virtualenv .venv
	source ./venv/bin/activate
	pip install -r dev-requirements.txt

clean:
	rm -rf .cache/ .tox/ *.egg-info *.key

dev:
	deps
	python setup.py develop

install:
	python setup.py install

test:
	pip install tox
	tox
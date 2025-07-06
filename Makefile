SHELL := bash

help:
	@echo  '  help            - Show this message'
	@echo  '  venv            - Create an empty Python3.13 virtual environment'
	@echo  '  install         - Install Bird ID Assistant package inside the created venv'
	@echo  '  dataset         - Scrape a dataset of bird species articles from Wikipedia'
	@echo  '  insert          - Insert the body texts from the scraped articles into a vector database'
	@echo
	@echo  '  flake            - (For development) Check code style with flake8'

.PHONY: install insert flake

venv:
	python3.13 -m venv --clear $@

install: venv
	$</bin/python3 -m pip install .

dataset:
	mkdir $@
	bia collect $@

insert: dataset
	bia db create $<

flake:
	flake8 src/

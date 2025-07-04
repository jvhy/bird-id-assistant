venv:
	python3.13 -m venv --clear $@

flake:
	flake8 src/

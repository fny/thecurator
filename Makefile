.PHONY: build
build:
	python setup.py sdist
	python setup.py bdist_wheel

.PHONY: clean
clean:
	rm -Rf dist build The_Curator.egg-info

.PHONY: setup
setup:
	pip install -r dev-requirements.txt

.PHONY: release
release: clean test build
	twine upload dist/*
	@echo "Don't forget to tag and push your release!"

.PHONY: release-test
release-test: clean test build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: test
test:
	python setup.py check -m -r -s
	pytest tests

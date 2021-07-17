.DEFAULT_GOAL := help
.PHONY: docs
SRC_DIRS = ./peddler ./tests ./bin
BLACK_OPTS = --exclude templates ${SRC_DIRS}

###### Development

docs: ## Build html documentation
	$(MAKE) -C docs

compile-requirements: ## Compile requirements files
	pip-compile requirements/base.in
	pip-compile requirements/dev.in
	pip-compile requirements/docs.in

upgrade-requirements: ## Upgrade requirements files
	pip-compile --upgrade requirements/base.in
	pip-compile --upgrade requirements/dev.in
	pip-compile --upgrade requirements/docs.in

build-pythonpackage: ## Build a python package ready to upload to pypi
	python setup.py sdist

push-pythonpackage: ## Push python package to pypi
	twine upload --skip-existing dist/peddler-$(shell make version).tar.gz

test: test-lint test-unit test-types test-format test-pythonpackage ## Run all tests by decreasing order or priority

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only --ignore=templates ${SRC_DIRS}

test-unit: ## Run unit tests
	python -m unittest discover tests

test-types: ## Check type definitions
	mypy --exclude=templates --ignore-missing-imports --strict peddler/ tests/

test-pythonpackage: build-pythonpackage ## Test that package can be uploaded to pypi
	twine check dist/peddler-$(shell make version).tar.gz

format: ## Format code automatically
	black $(BLACK_OPTS)

bootstrap-dev: ## Install dev requirements
# 	pip install .
	pip install -r requirements/dev.txt

bootstrap-dev-plugins: bootstrap-dev ## Install dev requirement and all supported plugins
	pip install -r requirements/plugins.txt

###### Deployment

bundle: ## Bundle the peddler package in a single "dist/peddler" executable
	pyinstaller peddler.spec

release: test ## Create a release tag and push it to origin
	$(MAKE) release-tag release-push TAG=v$(shell make version)
release-tag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
release-push:
	@echo "=== Pushing tag $(TAG) to origin"
	git push origin
	git push origin :$(TAG) || true
	git push origin $(TAG)

###### Continuous integration tasks

pull-base-images: # Manually pull base images
	docker image pull docker.io/ubuntu:20.04
	docker image pull docker.io/python:3.7-alpine

ci-info: ## Print info about environment
	python --version
	pip --version

ci-test-bundle: ## Run basic tests on bundle
	ls -lh ./dist/peddler
	./dist/peddler --version
	./dist/peddler config printroot
	yes "" | ./dist/peddler config save --interactive
	./dist/peddler config save
	# ./dist/peddler plugins list
	# ./dist/peddler plugins enable discovery ecommerce figures license minio notes xqueue
	# ./dist/peddler plugins enable discovery ecommerce license minio notes xqueue
	# ./dist/peddler plugins list
	# ./dist/peddler license --help

ci-push-bundle: ./releases/github-release ## Upload assets to github
	sed "s/PEDDLER_VERSION/v$(shell make version)/g" docs/_release_description.md > releases/description.md
	git log -1 --pretty=format:%b >> releases/description.md
	./releases/github-release release \
		--user alto9 \
		--repo peddler \
		--tag "v$(shell make version)" \
		--name "v$(shell make version)" \
		--description "$$(cat releases/description.md)" || true
	./releases/github-release upload \
	    --user alto9 \
	    --repo peddler \
	    --tag "v$(shell make version)" \
	    --name "peddler-$$(uname -s)_$$(uname -m)" \
	    --file ./dist/peddler \
			--replace

ci-bootstrap-images:
	pip install .
	peddler config save

###### Additional commands

version: ## Print the current peddler version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("peddler", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
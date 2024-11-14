build:
	poetry build
	pip install dist/*.tar.gz

create-dev:
	rm -rf env
	python3.10 -m venv env
	( \
		. env/bin/activate; \
		pip install -r requirements.txt; \
		poetry install; \
		deactivate; \
	)

create-output-dir:
	mkdir -p data/nature
	mkdir -p data/plos
	mkdir -p data/science

	mkdir -p data/nature/zettels
	mkdir -p data/plos/zettels
	mkdir -p data/science/zettels

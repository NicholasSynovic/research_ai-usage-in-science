build:
	git --no-pager tag | tail -n 1 | xargs -I % poetry version %
	poetry version --short > src/_version
	poetry build
	pip install dist/*.tar.gz

create-dev:
	pre-commit install
	rm -rf env
	python3.10 -m venv env
	( \
		. env/bin/activate; \
		pip install -r requirements.txt; \
		poetry install; \
		deactivate; \
	)

package:
	pyinstaller --clean \
		--onefile \
		--add-data ./src/_version:. \
		--workpath ./pyinstaller \
		--name aius\
		--hidden-import src \
		src/main.py

create-output-dir:
	mkdir -p data/nature
	mkdir -p data/plos
	mkdir -p data/science

	mkdir -p data/nature/zettels
	mkdir -p data/plos/zettels
	mkdir -p data/science/zettels

build:
	git --no-pager tag | tail -n 1 | xargs -I % poetry version %
	uv version --short > aius/_version
	uv build
	uv pip install dist/*.tar.gz

create-dev:
	pre-commit install
	pre-commit autoupdate
	rm -rf env
	uv sync

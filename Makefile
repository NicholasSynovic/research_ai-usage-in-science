build:
	rm -rf dist
	git tag | tr -s '[:blank:]' '\n' | sort | tail -n 1  | xargs -I % uv version %
	uv build
	uv pip install dist/*.tar.gz

create-dev:
	pre-commit install
	pre-commit autoupdate
	rm -rf env
	uv sync
